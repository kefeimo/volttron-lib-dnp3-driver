from volttron.client.vip.agent import build_agent
from volttron.utils.commands import vip_main
from volttron.client.vip.agent import Agent, Core


class TestAgent(Agent):
    def __init__(self, config_path, **kwargs):
        super().__init__(**kwargs)
        self.config_path = config_path


# def main():
#     """Main method called during startup of agent.
#     :return:"""
#     try:
#         a = vip_main(TestAgent, version=0.1)
#     except Exception as e:
#         print(f"unhandled exception {e}")
#     print()
#
#     # agent = ExampleAgent('example')
#     # print('1 ===========================')
#     # greenlet = gevent.spawn(agent.core.run)

def main():
    pass
    a = build_agent()
    print(a)

    peer = "platform_driver"

    # get_point example
    peer_method = "get_point"
    rs = a.vip.rpc.call(peer, peer_method, "campus-vm/building-vm/dnp3", "AnalogInput_index0").get(timeout=10)
    print(f"========== rs {rs}")

    # set_point example
    peer_method = "set_point"
    val = 4.6567
    rs = a.vip.rpc.call(peer, peer_method, "campus-vm/building-vm/dnp3", "AnalogOutput_index1", val).get(timeout=10)
    print(f"========== rs {rs}, val {val}")

    # # validation
    # peer_method = "get_point"
    # rs = a.vip.rpc.call(peer, peer_method, "campus-vm/building-vm/dnp3", "AnalogOutput_index0").get(timeout=10)
    # print(f"========== rs {rs}")


if __name__ == "__main__":
    main()
