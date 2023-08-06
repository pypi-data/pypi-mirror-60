from rest_framework import status

from zonesmart.marketplace.models import Channel
from zonesmart.marketplace.tests.factories import ChannelFactory
from zonesmart.tests.base import BaseViewSetTest


class ChannelViewTest(BaseViewSetTest):
    url_path = "zonesmart:marketplace:channel"

    @staticmethod
    def channel_to_dict(channel):
        return {
            "name": channel.name,
            "domain": channel.domain.id,
            "marketplace_user_account": channel.marketplace_user_account.id,
        }

    @staticmethod
    def delete_channels():
        Channel.objects.all().delete()

    def get_channel_list(self):
        url = self.get_url(postfix="list")
        return self.make_request(method="GET", url_path=url)

    def get_channel(self, channel_id):
        url = self.get_url(id=channel_id)
        return self.make_request(method="GET", url_path=url)

    def create_channel(self, channel):
        url = self.get_url(postfix="list")
        data = self.channel_to_dict(channel)
        return self.make_request(method="POST", url_path=url, data=data)

    def update_channel(self, channel):
        url = self.get_url(id=channel.id)
        data = self.channel_to_dict(channel)
        return self.make_request(method="PUT", url_path=url, data=data)

    def partial_update_channel(self, channel):
        url = self.get_url(id=channel.id)
        data = self.channel_to_dict(channel)
        return self.make_request(method="PATCH", url_path=url, data=data)

    def delete_channel(self, channel_id):
        url = self.get_url(id=channel_id)
        return self.make_request(method="DELETE", url_path=url)

    def test_get_channel_list(self):
        response = self.get_channel_list()
        self.assertStatus(response)

    def test_get_channel(self):
        channel = ChannelFactory.create()
        response = self.get_channel(channel_id=channel.id)
        self.assertStatus(response)
        self.assertEqual(channel.name, response.json()["name"])

    def test_create_channel(self):
        channel = ChannelFactory.create()
        self.delete_channels()
        self.assertEqual(Channel.objects.count(), 0)

        response = self.create_channel(channel=channel)
        self.assertStatus(response, status=status.HTTP_201_CREATED)

        self.assertEqual(Channel.objects.count(), 1)
        self.assertEqual(Channel.objects.filter(id=response.json()["id"]).count(), 1)

    def test_update_channel(self):
        """
        UpdateView and PartialUpdateView availability test
        """
        for method in [self.update_channel, self.partial_update_channel]:
            self.delete_channels()
            channel = ChannelFactory.create(name="Old name")
            new_name = "New name"
            channel.name = new_name

            self.assertEqual(Channel.objects.filter(name=new_name).count(), 0)
            response = self.update_channel(channel=channel)
            self.assertStatus(response)

            self.assertEqual(Channel.objects.filter(name=new_name).count(), 1)
            self.assertEqual(Channel.objects.get(id=channel.id).name, new_name)

    def test_delete_channel(self):
        """
        DeleteView availability test
        """
        channel = ChannelFactory.create()
        self.assertEqual(Channel.objects.filter(id=channel.id).count(), 1)

        response = self.delete_channel(channel_id=channel.id)
        self.assertStatus(response, status=status.HTTP_204_NO_CONTENT)

        self.assertEqual(Channel.objects.filter(id=channel.id).count(), 0)
