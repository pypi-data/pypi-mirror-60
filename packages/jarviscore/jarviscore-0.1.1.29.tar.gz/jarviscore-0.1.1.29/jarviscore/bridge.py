from .channel import Channel
from .httpclient import HTTPClient, WebResponse
from .log import Log
from time import sleep


api_users = "https://api.twitch.tv/helix/users?"

class Bridge():
    """description of class"""
    channels: list
    active: bool
    


    def __init__(self, client):
        self.client = client
        self.active = True
        self.web = HTTPClient("Bridge")
        self.log = Log("CORE")
        self.__init_channels()
        pass


    
    def __init_channels(self):
        self.channels = []
        chns = []
        for chn in self.__get_channel_shortlist():
            response: WebResponse = self.web.GetFromTwitch(api_users+chn)
            print(response)
            if response.code == 200 or response.code == "200":
                for user_data in response.json["data"]:
                    chns.append({
                        "login": user_data["login"],
                        "id": user_data["id"]
                    })
            else:
                self.log.error(f"There was an issue communicating with Twitch. Details: {response.message}")
        print(chns)
        for chan in chns:
            channel = Channel(self, self.client.nick, self.client.token, chan["login"], chan["id"])
            self.channels.append(channel)
            

    def __get_channel_shortlist(self):
        out = ""
        counter = 0
        maxCount = 80
        for chn in self.client.channels:
            if counter < maxCount:
                out += f"login={chn}&"
            else:
                yield out[:-1]
                out = f"login={chn}&"
                counter = 0
        yield out[:-1]


    def __get_channel(self, name: str):
        for channel in self.channels:
            if channel.name == name:
                return channel
        



    def run(self):
        try:
            for channel in self.channels:
                channel.start()
            while self.active:
                sleep(0.0001)
        except KeyboardInterrupt:         
            for channel in self.channels:
                channel.close()


    def check_messages(self):
        pass
    
    
    def add_channel(self, channel: str, id: int = None):
        if id is None:
            response: WebResponse = self.web.GetFromTwitch(f"{api_users}login={channel}")
            if response.code == 200 or response.code == "200":
                id = response.json["data"][0]["id"]
            else:
                self.log.error(f"Could not Add Channel. There was an issue communicating with Twitch. Details: {response.message}")
                return

        chn = Channel(self, self.client.nick, self.client.token, channel, id=id)
        self.channels.append(chn)
        chn.start()
        chn.on_new_connection(channel)
    
    def remove_channel(self, channel: str):
        for chn in self.channels:
            if chn.name == channel:
                chn.stop()
                self.channels.remove(chn)

    def leave_channel(self, channel: str):
        pass




    


