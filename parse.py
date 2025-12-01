from lxml import etree as ET
import html
import csv

print('starting script')
tree = ET.parse('recent.xml')

root = tree.getroot()

elements = {}

for update in root.findall('.//sys_update_xml'):
    action = update.findtext('.//action')    
    type = update.findtext('.//type')
    name = update.findtext('.//name')
    scope = update.find('.//application')
    scope = scope.get('display_value')
    table = update.findtext('.//table')

    payload = update.findtext('.//payload')

    if payload is None:
        continue

    payload = html.unescape(payload)
    payload.strip()

    if payload.startswith('<?xml'):
        payload = payload.split('?>', 1)[1].strip()

    payload_str = payload

    try:
        parser = ET.XMLParser(recover=True)
        inner_root = ET.fromstring(payload_str, parser=parser)

        sys_id = inner_root.findtext('.//sys_id')
        created = inner_root.findtext('.//sys_created_on')
        updated = inner_root.findtext('.//sys_updated_on')
        created_by = inner_root.findtext('.//sys_created_by').strip()
        updated_by = inner_root.findtext('.//sys_updated_by')
        display_name = inner_root.findtext('.//sys_name')
        internal_type_el = inner_root.find('.//internal_type')
        internal_type = None
        if internal_type_el is not None:
            internal_type = internal_type_el.get('display_value')
            if not internal_type:
                internal_type = internal_type_el.text

        if table is None or table == '':
            table = inner_root.get('table')

        if action == 'DELETE':
            if created_by == 'Optovia_dev2' or created_by == 'Optovia_dev' or created_by == 'Optovia_dev3' or created_by == 'winston.martinez' or created_by == 'G.R':
                if sys_id in elements:
                    del elements[sys_id]
                continue
            
        if action != 'DELETE' and (created_by == 'Optovia_dev2' or created_by == 'Optovia_dev' or created_by == 'Optovia_dev3' or created_by == 'winston.martinez' or created_by == 'G.R'):
            action = 'CREATE'
        elif action != 'DELETE':
            action = 'MODIFY'

        display_name = update.findtext('target_name')

        column_label = update.findtext('.//column_label')
        if column_label:
            display_name = column_label

        elements[sys_id] = [type or 'None', action or 'None', table or 'None', name or 'None', display_name or 'None', sys_id or 'None', scope or 'None', updated_by or 'None', updated or 'None', internal_type or 'None']

    except ET.XMLSyntaxError as e:
        print('invalid payload: ', e)

with open('output.csv', 'w') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    f.write('Type,Action,Table,Name,Display Name,Sys ID,Scope,Updated By, Updated On, Internal Type\n')
    for el in elements:
        if elements[el] is not None:
            writer.writerow(elements[el])
