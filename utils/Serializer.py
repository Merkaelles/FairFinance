class BaseSerializer:
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return {}


class ListSerializer:
    def __init__(self, data_list):
        self.data_list = data_list

    def dictlist_to_dict(self):
        if not self.data_list:
            return None
        if isinstance(self.data_list, list):
            self.data_list = dict(zip(data.keys(), data) for data in self.data_list)

    def to_dict(self):
        return {}


class PaginatorSerializer:
    def __init__(self, paginator):
        self.paginator = paginator
        if self.paginator:
            self.has_prev = self.paginator.has_prev
            self.has_next = self.paginator.has_next
            self.prev_num = self.paginator.prev_num
            self.next_num = self.paginator.next_num
            self.page = self.paginator.page
            self.pages = self.paginator.pages
            self.total = self.paginator.total
            self.per_page = self.paginator.per_page

    def get_obj(self, obj):
        return {}

    def page_info(self):
        return {
            'has_next': self.has_next,
            'has_prev': self.has_prev,
            'prev_num': self.prev_num,
            'next_num': self.next_num,
            'page': self.page,
            'pages': self.pages,
            'total': self.total,
            'per_page': self.per_page
        }

    def to_dict(self):
        page_info = self.page_info()
        page_data = []
        for item in self.paginator.items:
            page_data.append(self.get_obj(item))

        return {
            'page_info': page_info,
            'per_page': self.per_page,
            'page_data': page_data
        }


