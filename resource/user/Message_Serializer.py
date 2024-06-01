from utils.Serializer import PaginatorSerializer


class MessagePaginatorSerializer(PaginatorSerializer):
    def get_obj(self, obj):
        return {
            'id': obj.id,
            'sender': obj.sender,
            'content_id': obj.content_id,
            'title': obj.content.title,
            'content': obj.content.content,
            'send_time': obj.content.send_time.strftime('%Y-%m-%d %H:%M:%S'),
            'read_state': obj.read_state
        }
