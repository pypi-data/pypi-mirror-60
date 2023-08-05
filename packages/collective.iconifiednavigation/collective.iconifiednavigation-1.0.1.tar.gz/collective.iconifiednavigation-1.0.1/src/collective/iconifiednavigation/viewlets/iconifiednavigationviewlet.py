# encoding: utf-8
import os

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets.common import GlobalSectionsViewlet


class IconifiedNavigationViewlet(GlobalSectionsViewlet):
    index = ViewPageTemplateFile('iconifiednavigation-sections.pt')

    def relative_path(self, url):
        portal_url = api.portal.get_navigation_root(self.context).absolute_url()
        relative_path = url.replace(portal_url, '')
        if not relative_path:
            return ''
        if relative_path.startswith('/'):
            relative_path = relative_path[1:]
        return relative_path

    def get_object(self, url):
        path = self.relative_path(url)
        if not path:
            return None
        nav_root = api.portal.get_navigation_root(self.context)
        obj = nav_root.unrestrictedTraverse(path)
        return obj

    def get_image_infos(self, obj):
        if not obj:
            return
        icon = getattr(obj, 'navigation_icon', None)
        if not icon:
            return
        img_details = {}
        url = obj.absolute_url()
        name, ext = os.path.splitext(icon.filename)
        img_details["path"] = url + '/@@images/navigation_icon'
        img_details["ext"] = ext
        img_details["data"] = icon.data
        return img_details
