import hashlib

import zope.interface
import zope.component
import zope.file.file
import zope.file.download
import zope.file.interfaces
import zope.browser.interfaces
from zope.security.proxy import removeSecurityProxy

import zope.container.interfaces
import zope.filerepresentation.interfaces

import z3c.conditionalviews
import z3c.dav.coreproperties

class FileDAVSchema(object):
    """
      >>> from zope.interface.verify import verifyObject

      >>> f = zope.file.file.File('text/plain', {'charset': 'ascii'})
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

###############################################################################
#
# Define default view of the file object.
#
###############################################################################

class Display(zope.file.download.Display):

    @z3c.conditionalviews.ConditionalView
    def __call__(self):
        return super(Display, self).__call__()

################################################################################
#
# Define a FileFactory to make PUT work.
#
################################################################################

class FileFactory(object):
    """

      >>> f = FileFactory(None)
      >>> file = f('test', 'application/data', 'xxxxxxxxxx')
      >>> file.mimeType
      'application/data'
      >>> file.open('r').read()
      'xxxxxxxxxx'

    """
    zope.interface.implements(zope.filerepresentation.interfaces.IFileFactory)
    zope.component.adapts(zope.container.interfaces.IContainer)

    def __init__(self, container):
        pass

    def __call__(self, name, content_type, data):
        f = zope.file.file.File(mimeType = content_type)
        f.open("w").write(data)

        return f

################################################################################
#
# A slow but valid etag data source.
#
################################################################################

def getetag(context):
    # XXX - remove the security proxy so that we can view the context without
    # any security warnings. Should this be the case are can we configure the
    # system else where to avoid this.
    context = removeSecurityProxy(context)
    md5 = hashlib.md5()
    f = context.open("r")
    md5.update(f.read())
    f.close()
    return md5.hexdigest()


class ETag(object):
    """
      >>> from zope.interface.verify import verifyObject

      >>> f = zope.file.file.File('text/plain', {'charset': 'ascii'})
      >>> fp = f.open('w')
      >>> fp.write('y' * 20)
      >>> fp.close()

      >>> adapter = ETag(f, None, None) # request and view not needed

      >>> verifyObject(z3c.conditionalviews.interfaces.IETag, adapter)
      True
      >>> adapter.etag
      'abc161961f913fc9f32975a02320f6f9'
      >>> adapter.weak
      False

    """
    zope.interface.implements(z3c.conditionalviews.interfaces.IETag)
    zope.component.adapts(
        zope.file.interfaces.IFile,
        zope.publisher.interfaces.http.IHTTPRequest,
        zope.interface.Interface)

    def __init__(self, context, request, view):
        self.context = context

    weak = False

    @property
    def etag(self):
        return getetag(self.context)


class DAVETag(object):
    """
      >>> from zope.interface.verify import verifyObject

      >>> f = zope.file.file.File('text/plain', {'charset': 'ascii'})
      >>> fp = f.open('w')
      >>> fp.write('y' * 20)
      >>> fp.close()

      >>> adapter = DAVETag(f, None) # request not needed

      >>> verifyObject(z3c.dav.coreproperties.IDAVGetetag, adapter)
      True
      >>> adapter.getetag
      'abc161961f913fc9f32975a02320f6f9'

    """
    zope.interface.implements(z3c.dav.coreproperties.IDAVGetetag)
    zope.component.adapts(
        zope.file.interfaces.IFile,
        zope.publisher.interfaces.http.IHTTPRequest)

    def __init__(self, context, request):
        self.context = context

    @property
    def getetag(self):
        return getetag(self.context)
