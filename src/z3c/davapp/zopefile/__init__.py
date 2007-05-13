import zope.interface
import zope.component
import zope.file.interfaces

import z3c.dav.coreproperties


class FileDAVSchema(object):
    """
      >>> from zope.file.file import File
      >>> from zope.interface.verify import verifyObject

      >>> f = File('text/plain', {'charset': 'ascii'})
      >>> fp = f.open('w')
      >>> fp.write('y' * 20)
      >>> fp.close()

      >>> adapter = FileDAVSchema(f, None) # request not needed
      >>> verifyObject(z3c.dav.coreproperties.IDAVGetcontentlength, adapter)
      True
      >>> verifyObject(z3c.dav.coreproperties.IDAVGetcontenttype, adapter)
      True

      >>> adapter.getcontentlength
      20
      >>> adapter.getcontenttype
      'text/plain'

    """
    zope.interface.implements(z3c.dav.coreproperties.IDAVGetcontentlength,
                              z3c.dav.coreproperties.IDAVGetcontenttype)
    zope.component.adapts(zope.file.interfaces.IFile,
                          zope.publisher.interfaces.http.IHTTPRequest)

    def __init__(self, context, request):
        self.context = context

    @property
    def getcontentlength(self):
        return self.context.size

    @property
    def getcontenttype(self):
        return self.context.mimeType
