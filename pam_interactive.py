import pam
import getpass
from ctypes import c_int, c_size_t, c_char, c_char_p, c_void_p, py_object
from ctypes import sizeof, byref, cast, memmove, create_string_buffer
from ctypes import Structure, POINTER, CFUNCTYPE

class InteractivePamAuthenticator(pam.PamAuthenticator):
    def info(self, text: str):
        print(f"info: {text}")

    def error(self, text: str):
        print(f"error: {text}")

    def prompt(self, text: str) -> str:
        return input(text)

    def prompt_silent(self, text: str) -> str:
        return getpass.getpass(text)

    def __init__(self):
        super().__init__()

        pam_start_orig = self.pam_start

        PamConv = pam_start_orig.argtypes[2]._type_
        PamConv_fields = dict(PamConv._fields_)
        pam_conv_func = PamConv_fields["conv"]

        pp_PamMessage = pam_conv_func().argtypes[1]
        pp_PamResponse = pam_conv_func().argtypes[2]
        PamMessage = pp_PamMessage._type_._type_
        PamResponse = pp_PamResponse._type_._type_

        @pam_conv_func
        def pam_conv(n_messages: int, messages: pp_PamMessage, p_response: pp_PamResponse, p_app_data: c_void_p) -> int:
            # get encoding
            app_data = cast(p_app_data, py_object).value
            encoding: str = app_data.get('encoding')

            # calloc libc function
            calloc = self.libc.calloc
            calloc.restype = c_void_p
            calloc.argtypes = [c_size_t, c_size_t]

            # allocate response buffer
            response_buf = calloc(n_messages, sizeof(PamResponse))
            responses = cast(response_buf, POINTER(PamResponse))
            p_response[0] = responses

            for i in range(n_messages):
                message = messages[i].contents.msg
                message = message.decode(encoding)
                responses[i].resp = None
                responses[i].resp_retcode = 0

                response_str: str | None = None
                msg_style = messages[i].contents.msg_style
                if msg_style == pam.PAM_TEXT_INFO:
                    self.info(message)
                elif msg_style == pam.PAM_ERROR_MSG:
                    self.error(message)
                elif msg_style == pam.PAM_PROMPT_ECHO_ON:
                    response_str = self.prompt(message)
                elif msg_style == pam.PAM_PROMPT_ECHO_OFF:
                    response_str = self.prompt_silent(message)

                if response_str is not None:
                    response_bytes = response_str.encode(encoding)
                    response_cstr = calloc(len(response_bytes) + 1, sizeof(c_char))
                    memmove(response_cstr, response_bytes, len(response_bytes))
                    responses[i].resp = response_cstr

            return pam.PAM_SUCCESS

        def pam_start_wrapper(service, username, p_conv, p_handle):
            conv = cast(p_conv, POINTER(PamConv)).contents
            conv.conv = pam_conv

            return pam_start_orig(service, username, p_conv, p_handle)

        self.pam_start = pam_start_wrapper

    def authenticate(
        self,
        username: str | bytes,
        service: str | bytes = 'login',
        env: dict | None = None,
        call_end: bool = True,
        encoding: str = 'utf-8',
        resetcreds: bool = True,
        print_failure_messages: bool = False
    ) -> bool:
        return super().authenticate(username, "", service, env, call_end, encoding, resetcreds, print_failure_messages)
