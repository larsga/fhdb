
import proclib

def bv(v):
    if v == proclib.BORDERLINE:
        return '~'
    elif v == None:
        return '?'
    elif v:
        return 'Y'
    else:
        return 'N'

def iv(v):
    return v if v != None else '?'

f = open('proctable.html', 'w')
f.write('''
<style>
td, th { padding-right: 6pt }
</style>
<table>
<tr><th>No <th>Name <th>I <th>C <th>MK <th>MB <th>S <th>O <th>B <th>Cat <th>Heat
''')

for proc in proclib.load_processes():
    f.write('''
        <tr><td>%s <td><span title="%s">%s <td>%s <td>%s <td>%s <td>%s
            <td>%s <td>%s <td>%s <td>%s <td>%s
    ''' % (proc.get_no(), proc.get_desc(), proc.get_name(), iv(proc._inf),
           iv(proc._circ), bv(proc._mashkettle), bv(proc._mashboil),
           bv(proc._stones), bv(proc._inoven), bv(proc._wboil),
           proc.get_category(), proc.get_main_heating() or '')
    )

f.write('</table>\n')
