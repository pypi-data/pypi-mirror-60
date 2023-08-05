from gitlabagent import BaseObject

class WebhookObject(BaseObject):

    def __init__(self,
                    object_kind,
                    before = None,
                    after = None,
                    ref = None,
                    checkout_sha = None,
                    user_id = None,
                    user_name = None,
                    user_username = None,
                    user_email = None,
                    user_avatar = None,
                    project_id = None,
                    project = None,
                    repository = None,
                    commits = None,
                    total_commits_count = None, **kwargs):
        #primary
        self.object_kind = object_kind
        #Optional
        self.before = before
        self.after = after
        self.ref = ref
        self.checkout_sha = checkout_sha
        self.user_id = user_id
        self.user_name = user_name
        self.user_username = user_username
        self.user_email = user_email
        self.user_avatar = user_avatar
        self.project_id = project_id
        self.project = project
        self.repository = repository
        self.commits = commits
        self.total_commits_count = total_commits_count

    @classmethod
    def decode_json(cls, data):
        if not data:
            return None

        data = super(WebhookObject, cls).decode_json(data)

        return cls(**data)
