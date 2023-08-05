from xml.dom.minidom import parse
import xml.dom.minidom
import logging
from ..indicators import classes
from ..generator import BIG

logger = logging.getLogger(__name__)
counts = {

}


def parseXMLToIndicators(filename):
    DOMTree = xml.dom.minidom.parse(filename)
    indicators = DOMTree.getElementsByTagName('indicator')
    indicator_list = []

    for name in classes.keys():
        counts[name] = 0

    for indicator in indicators:
        label = indicator.getAttribute('label')
        class_name = indicator.getAttribute('class').upper()

        if label == '':
            label = 'None'

        if class_name not in classes.keys():
            logger.warning(f'invalid indicator class:{class_name} with label:{label},allowed:{classes.keys()}')
            continue

        if label == 'None':
            label = class_name + f'_{counts[class_name]}'
            counts[class_name] += 1

        iclass = classes[class_name]

        params_tag = indicator.getElementsByTagName('parameters')

        if len(params_tag) == 0:
            logger.warning(f'Indicator {label} has no parameters')
            continue

        params_tag = params_tag[0]
        params = params_tag.getElementsByTagName('parameter')
        plist = []
        for i, param_tag in enumerate(params):
            l = param_tag.childNodes[0].data.split(',')
            plist.append(l)

        new_plist = []
        if len(plist) > 0:
            for i, p_value in enumerate(plist[0]):
                v_list = []
                for p in plist:
                    v_list.append(eval(p[i]))
                new_plist.append(v_list)

        sources_list = []

        sources_tags = indicator.getElementsByTagName('sources')

        if len(sources_tags) == 0:
            logger.warning(f'Indicator {label} has no sources')

        for sources_tag in sources_tags:
            for source_tag in sources_tag.getElementsByTagName('source'):
                source = source_tag.childNodes[0].data.split(',')
                sources_list.append(source)

        i = BIG(iclass, new_plist, sources_list)
        indicator_list.extend(i)
    return indicator_list


