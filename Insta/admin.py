from django.contrib import admin
from Insta.models import Post, InstaUser, Like, UserConnection, Comment

#register your model here
admin.site.register(Post)
admin.site.register(InstaUser)
admin.site.register(Like)
admin.site.register(UserConnection)
admin.site.register(Comment)
