import sys
import pyrap.quanta as qa
import pyrap.tables as pt
import pyrap.measures as pm
import numpy

from check_Ateam_separation import input2strlist_nomapfile

from connect_to_qa_table import add_qa_note

            
def generate_note_1(ms_input):
    note = ""
    
    targets = [ {'name' : 'CasA', 'ra' : 6.123487680622104,  'dec' : 1.0265153995604648},
            {'name' : 'CygA', 'ra' : 5.233686575770755,  'dec' : 0.7109409582180791},
            {'name' : 'TauA', 'ra' : 1.4596748493730913, 'dec' : 0.38422502335921294},
            {'name' : 'HerA', 'ra' : 4.4119087330382163, 'dec' : 0.087135562905816893},
            {'name' : 'VirA', 'ra' : 3.276086511413598,  'dec' : 0.21626589533567378},
            {'name' : 'Sun'},
            {'name' : 'Jupiter'},
            {'name' : 'Moon'}]
    
    msname = input2strlist_nomapfile(ms_input)[0]
    min_separation = 30
  
    # Create a measures object
    me = pm.measures()

    # Open the measurement set and the antenna and pointing table
    ms = pt.table(msname)  

    # Get the position of the first antenna and set it as reference frame
    ant_table = pt.table(msname + '::ANTENNA')  
    ant_no = 0
    pos = ant_table.getcol('POSITION')
    x = qa.quantity( pos[ant_no,0], 'm' )
    y = qa.quantity( pos[ant_no,1], 'm' )
    z = qa.quantity( pos[ant_no,2], 'm' )
    position =  me.position( 'wgs84', x, y, z )
    me.doframe( position )
    ant_table.close()

    # Get the first pointing of the first antenna
    field_table = pt.table(msname + '::FIELD')
    field_no = 0
    direction = field_table.getcol('PHASE_DIR')
    ra = direction[ ant_no, field_no, 0 ]
    dec = direction[ ant_no, field_no, 1 ]
    targets.insert(0, {'name' : 'Pointing', 'ra' : ra, 'dec' : dec})
    field_table.close()

    # Get a ordered list of unique time stamps from the measurement set
    time_table = pt.taql('select TIME from $1 orderby distinct TIME', tables = [ms])
    time = time_table.getcol('TIME')
    #time1 = time/3600.0
    #time1 = time1 - pylab.floor(time1[0]/24)*24

    ra_qa  = qa.quantity( targets[0]['ra'], 'rad' )
    dec_qa = qa.quantity( targets[0]['dec'], 'rad' )
    pointing =  me.direction('j2000', ra_qa, dec_qa)
    
    separations = []
    elevations = []
    
    for target in targets:
        t = qa.quantity(time[0], 's')
        t1 = me.epoch('utc', t)
        me.doframe(t1)

        if 'ra' in target.keys():
            ra_qa  = qa.quantity( target['ra'], 'rad' )
            dec_qa = qa.quantity( target['dec'], 'rad' )
            direction =  me.direction('j2000', ra_qa, dec_qa)
        else :
            direction =  me.direction(target['name'])
      
        separations.append(me.separation(pointing, direction))

        # Loop through all time stamps and calculate the elevation of the pointing
        el = []
        for t in time:
            t_qa = qa.quantity(t, 's')
            t1 = me.epoch('utc', t_qa)
            me.doframe(t1)
            a = me.measure(direction, 'azel')
            elevation = a['m1']
            el.append(elevation['value']/numpy.pi*180)
        
        el = numpy.array(el)
        elevations.append(numpy.mean(el))
        
        if target['name'] != 'Pointing':
            if int(float(min_separation)) >  int(float(str(me.separation(pointing, direction)).split(' deg')[0])):
                note += 'The A-Team source ' + target['name'] + ' is closer than ' + str(min_separation) + ' deg to the phase reference center. Calibration might not perform as expected.'
        else:
            if numpy.mean(el) < 30:
                note += 'Elevation of pointing is less than 30 deg'
            
	if elevations[0] < any (elevations[1:len(elevations)]):
		note += 'Elevation of pointing is less that one of A-Team sources'
    return note
    
    
def generate_note_6(prefactor_log):
    note = ""
	
    bad_stations = []
    line_index = -1
    with open(prefactor_log) as log:
        lines = log.readlines()
        end_line_index = len(lines) -1
        for line in lines:
            line_index += 1
            if "Overall amount of flagged data in the final data:" in line:
                for l in range(line_index + 2, end_line_index):
                    station = lines[l].split()[0]
                    flag_amount = lines[l].split()[1]
                    if "100.00%" in flag_amount:
                        bad_stations.append(station)
                        
    if len(bad_stations) != 0:
        note = "These stations are fully flagged"             
    for s in bad_stations:
        note += " " + s 
    return note


def main(ms_input, prefactor_log):
    note = generate_note_1(ms_input) + " " + generate_note_6(prefactor_log)
    if len(note) == 0:
		note = "everything is OK"
	
    add_qa_note(note, "H232+29", "calibrator")	
    print(note)
    sys.exit(0)


if __name__ == "__main__":
    ms_input = "L167225_SAP000_SB000_uv.MS"
    prefactor_log = "Pre-Facet-Calibrator.log"
    main(ms_input, prefactor_log)
