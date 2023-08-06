from applauncher.kernel import ConfigurationReadyEvent
from slackclient import SlackClient
import inject


class SlackBundle(object):
    def __init__(self):
        self.config_mapping = {
            "slack": {
                "token": None,
            }
        }

        self.event_listeners = [
            (ConfigurationReadyEvent, self.configuration_ready),
            (KernelReadyEvent, self.kernel_ready),
            (KernelShutdownEvent, self.kernel_shutdown),
        ]

        self.injection_bindings = {}

    def configuration_ready(self, event):
        self.injection_bindings[SlackClient] = SlackClient(token=event.configuration.slack.token)
