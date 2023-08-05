# -*- coding: utf-8 -*-
from csv import reader
from csv import writer
from Products.GenericSetup.content import _globtest
from Products.GenericSetup.content import FauxDAVRequest
from Products.GenericSetup.content import FauxDAVResponse
from Products.GenericSetup.content import FolderishExporterImporter
from Products.GenericSetup.interfaces import IContentFactoryName
from Products.GenericSetup.interfaces import IFilesystemExporter
from Products.GenericSetup.interfaces import IFilesystemImporter
from Products.GenericSetup.utils import _getDottedName
from six import StringIO
from zope.component import queryAdapter
from zope.interface import implementer


def import_(self, import_context, subdir, root=False):
    """ See IFilesystemImporter.
    """
    context = self.context
    if not root:
        subdir = '%s/%s' % (subdir, context.getId())

    data = import_context.readDataFile('.data', subdir)
    if data is not None:
        data = data.decode('utf-8')
        request = FauxDAVRequest(BODY=data, BODYFILE=StringIO(data))
        response = FauxDAVResponse()
        context.PUT(request, response)

    preserve = import_context.readDataFile('.preserve', subdir)
    if preserve:
        preserve = preserve.decode('utf-8')
    must_preserve = self._mustPreserve()

    prior = context.objectIds()

    if not preserve:
        preserve = []
    else:
        preserve = _globtest(preserve, prior)

    preserve.extend([x[0] for x in must_preserve])

    for id in prior:
        if id not in preserve:
            context._delObject(id)

    objects = import_context.readDataFile('.objects', subdir)
    if objects is None:
        return
    else:
        objects = objects.decode('utf-8')

    dialect = 'excel'
    stream = StringIO(objects)

    rowiter = reader(stream, dialect)
    rows = filter(None, tuple(rowiter))

    existing = context.objectIds()

    for object_id, type_name in rows:

        if object_id not in existing:
            object = self._makeInstance(object_id, type_name,
                                        subdir, import_context)
            if object is None:
                logger = import_context.getLogger('SFWA')
                logger.warning("Couldn't make instance: %s/%s" %
                               (subdir, object_id))
                continue

        wrapped = context._getOb(object_id)

        adapted = queryAdapter(wrapped, IFilesystemImporter)
        if adapted is not None:
            adapted.import_(import_context, subdir)
