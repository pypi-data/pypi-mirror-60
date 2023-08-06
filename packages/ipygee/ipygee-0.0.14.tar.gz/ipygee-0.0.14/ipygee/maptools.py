# coding=utf-8

""" Tools for the Map """

import ee
from geetools import tools
import math
from uuid import uuid4


def getBounds(eeObject):
    if isinstance(eeObject, list):
        bounds = eeObject
    else:
        # Make a buffer if object is a Point
        if isinstance(eeObject, ee.Geometry):
            t = eeObject.type().getInfo()
            if t == 'Point':
                eeObject = eeObject.buffer(1000)

        bounds = tools.geometry.getRegion(eeObject, True)

    # Catch unbounded images
    unbounded = [[[-180.0, -90.0], [180.0, -90.0],
                  [180.0, 90.0], [-180.0, 90.0],
                  [-180.0, -90.0]]]

    if bounds == unbounded:
        print("can't center object because it is unbounded")
        return None

    bounds = inverseCoordinates(bounds)
    return bounds


def getDefaultVis(image, stretch=0.8):
    bandnames = image.bandNames().getInfo()

    if len(bandnames) < 3:
        selected = image.select([0]).getInfo()
        bandnames = bandnames[0]
    else:
        selected = image.select([0, 1, 2]).getInfo()
        bandnames = [bandnames[0], bandnames[1], bandnames[2]]

    bands = selected['bands']
    # bandnames = [bands[0]['id'], bands[1]['id'], bands[2]['id']]
    types = bands[0]['data_type']

    maxs = {'float':1,
            'double': 1,
            'int8': 127, 'uint8': 255,
            'int16': 32767, 'uint16': 65535,
            'int32': 2147483647, 'uint32': 4294967295,
            'int64': 9223372036854776000}

    precision = types['precision']

    if precision == 'float':
        btype = 'float'
    elif precision == 'double':
        btype = 'double'
    elif precision == 'int':
        max = types['max']
        maxs_inverse = dict((val, key) for key, val in maxs.items())
        btype = maxs_inverse[int(max)]
    else:
        raise ValueError('Unknown data type {}'.format(precision))

    limits = {'float': 0.8}

    for key, val in maxs.items():
        limits[key] = val*stretch

    min = 0
    max = limits[btype]
    return {'bands':bandnames, 'min':min, 'max':max}


def isPoint(item):
    """ Determine if the given list has the structure of a point. This is:
    it is a list or tuple with two int or float items """
    if isinstance(item, list) or isinstance(item, tuple):
        if len(item) == 2:
            lon = item[0]
            if isinstance(lon, int) or isinstance(lon, float):
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def inverseCoordinates(coords):
    """ Inverse a set of coordinates (any nesting depth)

    :param coords: a nested list of points
    :type coords: list
    """
    newlist = []
    if isPoint(coords):
        return [coords[1], coords[0]]
    elif not isinstance(coords, list) and not isinstance(coords, tuple):
        raise ValueError('coordinates to inverse must be minimum a point')
    for i, it in enumerate(coords):
        p = isPoint(it)
        if not p and (isinstance(it, list) or isinstance(it, tuple)):
            newlist.append(inverseCoordinates(it))
        else:
            newp = [it[1],it[0]]
            newlist.append(newp)
    return newlist


def visparamsStrToList(params):
    """ Transform a string formated as needed by ee.data.getMapId to a list

    :param params: params to convert
    :type params: str
    :return: a list with the params
    :rtype: list
    """
    proxy_bands = []
    bands = params.split(',')
    for band in bands:
        proxy_bands.append(band.strip())
    return proxy_bands


def visparamsListToStr(params):
    """ Transform a list to a string formated as needed by
        ee.data.getMapId

    :param params: params to convert
    :type params: list
    :return: a string formated as needed by ee.data.getMapId
    :rtype: str
    """
    n = len(params)
    if n == 1:
        newbands = '{}'.format(params[0])
    elif n == 3:
        newbands = '{},{},{}'.format(params[0], params[1], params[2])
    else:
        newbands = '{}'.format(params[0])
    return newbands


def getImageTile(image, visParams, show=True, opacity=None,
                 overlay=True):

    proxy = {}
    params = visParams if visParams else {}

    # BANDS #############
    def default_bands(image):
        bandnames = image.bandNames().getInfo()
        if len(bandnames) < 3:
            bands = [bandnames[0]]
        else:
            bands = [bandnames[0], bandnames[1], bandnames[2]]
        return bands
    bands = params.get('bands') if 'bands' in params else default_bands(image)

    # if the passed bands is a string formatted like required by GEE, get the
    # list out of it
    if isinstance(bands, str):
        bands_list = visparamsStrToList(bands)
        bands_str = visparamsListToStr(bands_list)

    # Transform list to getMapId format
    # ['b1', 'b2', 'b3'] == 'b1, b2, b3'
    if isinstance(bands, list):
        bands_list = bands
        bands_str = visparamsListToStr(bands)

    # Set proxy parameteres
    proxy['bands'] = bands_str

    # MIN #################
    themin = params.get('min') if 'min' in params else '0'

    # if the passed min is a list, convert to the format required by GEE
    if isinstance(themin, list):
        themin = visparamsListToStr(themin)

    proxy['min'] = themin

    # MAX #################
    def default_max(image, bands):
        proxy_maxs = []
        maxs = {'float':1,
                'double': 1,
                'int8': ((2**8)-1)/2, 'uint8': (2**8)-1,
                'int16': ((2**16)-1)/2, 'uint16': (2**16)-1,
                'int32': ((2**32)-1)/2, 'uint32': (2**32)-1,
                'int64': ((2**64)-1)/2}
        for band in bands:
            ty = image.select([band]).getInfo()['bands'][0]['data_type']
            try:
                themax = maxs[ty]
            except:
                themax = 1
            proxy_maxs.append(themax)
        return proxy_maxs

    themax = params.get('max') if 'max' in params else default_max(image,
                                                                   bands_list)

    # if the passed max is a list or the max is computed by the default function
    # convert to the format required by GEE
    if isinstance(themax, list):
        themax = visparamsListToStr(themax)

    proxy['max'] = themax

    # PALETTE ################
    if 'palette' in params:
        if len(bands_list) == 1:
            palette = params.get('palette')
            if isinstance(palette, str):
                palette = visparamsStrToList(palette)
            toformat = '{},'*len(palette)
            palette = toformat[:-1].format(*palette)
            proxy['palette'] = palette
        else:
            print("Can't use palette parameter with more than one band")

    # Get the MapID and Token after applying parameters
    image_info = image.getMapId(proxy)
    fetcher = image_info['tile_fetcher']
    tiles = fetcher.url_format
    attribution = 'Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a> '
    overlay = overlay

    return {'url': tiles,
            'attribution': attribution,
            'overlay': overlay,
            'show': show,
            'opacity': opacity,
            'visParams': proxy,
            }


def featurePropertiesOutput(feat):
    """ generates a string for features properties """
    info = feat.getInfo()
    properties = info['properties']
    theid = info.get('id')
    if theid:
        stdout = '<h3>ID {}</h3></br>'.format(theid)
    else:
        stdout = '<h3>Feature has no ID</h3></br>'

    if properties:
        for prop, value in properties.items():
            stdout += '<b>{}</b>: {}</br>'.format(prop, value)
    else:
        stdout += '<b>Feature has no properties</b>'
    return stdout


def getGeojsonTile(geometry, name=None,
                   inspect={'data':None, 'reducer':None, 'scale':None}):
    ''' Get a GeoJson giving a ee.Geometry or ee.Feature '''

    if isinstance(geometry, ee.Feature):
        feat = geometry
        geometry = feat.geometry()
    else:
        feat = None

    info = geometry.getInfo()
    type = info['type']

    gjson_types = ['Polygon', 'LineString', 'MultiPolygon',
                   'LinearRing', 'MultiLineString', 'MultiPoint',
                   'Point', 'Polygon', 'Rectangle',
                   'GeometryCollection']

    # newname = name if name else "{} {}".format(type, map.added_geometries)

    if type in gjson_types:
        data = inspect['data']
        if feat:
            default_popup = featurePropertiesOutput(feat)
        else:
            default_popup = type
        red = inspect.get('reducer','first')
        sca = inspect.get('scale', None)
        popval = getData(geometry, data, red, sca, name) if data else default_popup
        geojson = geometry.getInfo()

        return {'geojson':geojson,
                'pop': popval}
        # 'name': newname}
    else:
        print('unrecognized object type to add to map')


def getZoom(bounds, method=1):
    '''
    as ipyleaflet does not have a fit bounds method, try to get the zoom to fit

    from: https://stackoverflow.com/questions/6048975/google-maps-v3-how-to-calculate-the-zoom-level-for-a-given-bounds
    '''
    bounds = bounds[0]
    sw = bounds[0]
    ne = bounds[2]

    sw_lon = sw[1]
    sw_lat = sw[0]
    ne_lon = ne[1]
    ne_lat = ne[0]

    def method1():
        # Method 1
        WORLD_DIM = {'height': 256, 'width': 256}
        ZOOM_MAX = 21

        def latRad(lat):
            sin = math.sin(lat * math.pi / 180)
            radX2 = math.log((1 + sin) / (1 - sin)) / 2
            return max(min(radX2, math.pi), -math.pi) / 2

        def zoom(mapPx, worldPx, fraction):
            return math.floor(math.log(mapPx / worldPx / fraction) / math.log(2))

        latFraction = float(latRad(ne_lat) - latRad(sw_lat)) / math.pi

        lngDiff = ne_lon - sw_lon

        lngFraction = (lngDiff + 360) if (lngDiff < 0) else lngDiff
        lngFraction = lngFraction / 360

        latZoom = zoom(400, WORLD_DIM['height'], latFraction)
        lngZoom = zoom(970, WORLD_DIM['width'], lngFraction)

        return int(min(latZoom, lngZoom, ZOOM_MAX))

    def method2():
        scale = 111319.49

        GLOBE_WIDTH = 256 # a constant in Google's map projection

        angle = ne_lon - sw_lon
        if angle < 0:
            angle += 360
        zoom = math.floor(math.log(scale * 360 / angle / GLOBE_WIDTH) / math.log(2))
        return int(zoom)-8

    finalzoom = method1() if method == 1 else method2()
    return finalzoom


# TODO: Multiple dispatch! https://www.artima.com/weblogs/viewpost.jsp?thread=101605
def getData(geometry, obj, reducer='first', scale=None, name=None):
    ''' Get data from an ee.ComputedObject using a giving ee.Geometry '''
    accepted = (ee.Image, ee.ImageCollection, ee.Feature, ee.FeatureCollection)

    reducers = {'first': ee.Reducer.first(),
                'mean': ee.Reducer.mean(),
                'median': ee.Reducer.median(),
                'sum':ee.Reducer.sum()}

    if not isinstance(obj, accepted):
        return "Can't get data from that Object"
    elif isinstance(obj, ee.Image):
        t = geometry.type().getInfo()
        # Try to get the image scale
        scale = obj.select([0]).projection().nominalScale().getInfo() \
            if not scale else scale

        # Reduce if computed scale is too big
        scale = 1 if scale > 500 else scale
        if t == 'Point':
            values = tools.image.getValue(obj, geometry, scale, 'client')
            val_str = '<h3>Data from {}'.format(name)
            for key, val in values.items():
                val_str += '<b>{}:</b> {}</br>'.format(key, val)
            return val_str
        elif t == 'Polygon':
            red = reducer if reducer in reducers.keys() else 'first'
            values = obj.reduceRegion(reducers[red], geometry, scale, maxPixels=1e13).getInfo()
            val_str = '<h3>{}:</h3>\n'.format(red)
            for key, val in values.items():
                val_str += '<b>{}:</b> {}</br>'.format(key, val)
            return val_str


def paint(geometry, outline_color='black', fill_color=None, outline=2):
    """ Paint a Geometry, Feature or FeatureCollection """

    def overlap(image_back, image_front):
        mask_back = image_back.mask()
        mask_front = image_front.mask()
        entire_mask = mask_back.add(mask_front)
        mask = mask_back.Not()
        masked = image_front.updateMask(mask).unmask()

        return masked.add(image_back.unmask()).updateMask(entire_mask)

    if isinstance(geometry, ee.Feature) or isinstance(geometry, ee.FeatureCollection):
        geometry = geometry.geometry()

    if fill_color:
        fill = ee.Image().paint(geometry, 1).visualize(palette=[fill_color])

    if outline_color:
        out = ee.Image().paint(geometry, 1, outline).visualize(palette=[outline_color])

    if fill_color and outline_color:
        rgbVector = overlap(out, fill)
    elif fill_color:
        rgbVector = fill
    else:
        rgbVector = out

    return rgbVector


def createHTMLTable(header, rows):
    ''' Create a HTML table

    :param header: a list of headers
    :type header: list
    :param rows: a list with the values
    :type rows: list
    :return: a HTML string
    :rtype: str
    '''
    uid = 'a'+uuid4().hex
    style = '<style>\n.{}\n{{border: 1px solid black;\n border-collapse: collapse;}}\n</style>\n'
    style = style.format(uid)
    general = '<table class="{}">\n{{}}</table>'.format(uid)
    row = '  <tr class="{}">\n{{}}</tr>\n'.format(uid)
    col = '    <td style="text-align: center" class="{}">{{}}</td>\n'.format(uid)
    headcol = '    <th class="{}">{{}}</th>\n'.format(uid)

    # header
    def create_row(alist, template):
        cols = ''
        for el in alist:
            cols += template.format(el)
        newrow = row.format(cols)
        return newrow

    header_row = create_row(header, headcol)

    rest = ''
    # rows
    for r in rows:
        newrow = create_row(r, col)
        rest += newrow

    body = '{}\n{}'.format(header_row, rest)
    html = '{}\n{}'.format(style, general.format(body))

    return html