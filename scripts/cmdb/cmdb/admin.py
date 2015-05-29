from django.contrib import admin
from cmdb.models import Service
from cmdb.forms import ServiceForm
import threading, time
import zmq, json


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('ip', 'port', 'proto')
    search_fields = ['ip', 'proto']

    form = ServiceForm
    context = zmq.Context()

    def save_model(self, request, obj, form, change):
        #file_object = open('/var/log/test2.txt', 'w+')

        obj.user = request.user
        obj.save()

        sender = self.context.socket(zmq.PUSH)
        sender.connect("tcp://localhost:60008")
        msg = obj.get_fields()
        if change :
            msg['command'] = 'update'
        else :
            msg['command'] = 'add'

        sender.send (json.dumps(msg))

        #file_object.close()

    def delete_selected_services(self, request, QuerySet):
        #file_object = open('/var/log/test2.txt', 'w+')

        for obj in QuerySet :
            obj.user = request.user
            #file_object.write("obj: %s\n\n" % str(obj.get_fields()))
            msg = obj.get_fields()
            msg['command'] = 'delete'
            obj.delete()

            sender = self.context.socket(zmq.PUSH)
            sender.connect("tcp://localhost:60008")
            sender.send (json.dumps(msg))

        #file_object.close()

    def get_actions(self, request):
        actions = super(ServiceAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    actions = [delete_selected_services]

admin.site.register(Service, ServiceAdmin)
