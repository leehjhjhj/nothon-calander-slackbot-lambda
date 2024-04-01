from slack_sdk import WebClient
from datetime import datetime
import dateutil.tz

class SendToSlackAPI:
    """
    slack 메시지 API
    """
    def __init__(self, token, channel_id):
        self.client = WebClient(token)
        self.channel_id = channel_id

    def send_message(self, message):
        result = self.client.chat_postMessage(
            channel = self.channel_id,
            blocks = [{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }]
        )
        return result
    
class AttendencyCheck:
    def __init__(self, slack_token, channel_id):
        self._slack_token = slack_token
        self._client = WebClient(self._slack_token)
        self._channel_id = channel_id
        self._send_client = SendToSlackAPI(self._slack_token, self._channel_id)

    def make_and_send_absent_message(self):
        attendenced_users = self._get_yesterday_attendenced_users()
        if attendenced_users:
            attendenced_users_set = set(attendenced_users)
            slack_users = self._get_slack_users()
            absent_users_list = []
            absent_users = ''
            
            for slack_user_name, slack_user_id in slack_users.items():
                    if slack_user_id not in attendenced_users_set:
                        absent_users += slack_user_name + ', '
                        absent_users_list.append(slack_user_name)
            if absent_users_list:
                message = f":face_with_rolling_eyes: 이러언… ! 어제 슬랙을 안 한 팀원 분들이에요.\n [{absent_users}] \n오늘은 꼭 해주세요 ~ "
            else:
                message = f":smiling_face_with_3_hearts: 우와우 ~ 어제는 모두가 출첵을 했어요! 이 기세를 몰아 오늘도 모두 출석해보아요 :sunglasses:"
        else:
            message = ":rage: 이게 무슨 일이람? 다들 겨울 잠을 자고 있는 건가요? 잠에서 깨어나세요! :triumph:"
        self._send_client.send_message(message)

    def make_and_send_attendency_check_message(self):
        now = datetime.now(dateutil.tz.gettz('Asia/Seoul'))
        formatted_date = now.strftime("%-m월 %d일")
        message = f":white_check_mark:  [{formatted_date} 출석체크] 좋은 아침이에요! 모두 슬랙 메시지 한번 확인해주시고 따봉 이모지 부탁드릴게요 :hugging_face:"
        self._send_client.send_message(message)

    def _get_yesterday_attendenced_users(self):
        response = self._client.conversations_history(channel=self._channel_id, limit=10)
        messages = response.get('messages')
        users: list[str] = None
        for message in messages:
            text: str = message.get('text')
            if ':white_check_mark:' in text:
                reactions = message.get('reactions', None)
                if reactions:
                    users = reactions[0].get('users')
                break
        return users

    def _get_slack_users(self):
        response = self._client.users_list()
        if response['ok']:
            members = response['members']
            name_id_map = {}
            for member in members:
                if member.get('real_name') != 'Slackbot' and not member.get('is_bot'):
                    id = member.get('id')
                    name = member.get('real_name')
                    name_id_map[f'{name}'] = id
            return name_id_map
        else:
            return None