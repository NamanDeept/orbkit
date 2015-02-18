# -*- coding: iso-8859-1 -*-
'''Module for creating the requested output files.
'''
'''
orbkit
Gunter Hermann, Vincent Pohl, and Axel Schild

Institut fuer Chemie und Biochemie, Freie Universitaet Berlin, 14195 Berlin, Germany

This file is part of orbkit.

orbkit is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of 
the License, or any later version.

orbkit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public 
License along with orbkit.  If not, see <http://www.gnu.org/licenses/>.
'''

# Import general modules
import numpy
import h5py

# Import orbkit modules
from orbkit import grid, options
from orbkit.display import display

def main_output(data,geo_info,geo_spec,outputname='new',otype='h5',
                drv=None,omit=[],is_vector=False,**kwargs):
  '''Creates the requested output.
  '''
  print_waring = False
  output_written = []
  if drv is not None:
    fid = '%(f)s_d%(d)s'
    it = enumerate(drv)
  else:
    fid = '%(f)s'
    it = [(0,None)]
    data = [data]
  f = {'f': outputname}
  
  for i,j in it:
    f['d'] = j
    d = data[i]
    if 'h5' in otype and 'h5' not in omit:
      display('\nSaving to Hierarchical Data Format file (HDF5)...' +
              '\n\t%(o)s.h5' % {'o': fid % f})
      HDF5_creator(d,(fid % f),geo_info,geo_spec,**kwargs)
      output_written.append('%s.h5' % (fid % f))
    if 'am' in otype or 'hx' in otype and not print_waring:
      if is_vector: print_waring = True
      else: 
        display('\nSaving to ZIBAmiraMesh file...' +
                     '\n\t%(o)s.am' % {'o': fid % f})
        amira_creator(d,(fid % f))
        output_written.append('%s.am' % (fid % f))
    if 'hx' in otype and not print_waring:
      if is_vector: print_waring = True
      else: 
        # Create Amira network incl. Alphamap
        display('\nCreating ZIBAmira network file...')
        hx_network_creator(data,(fid % f))
        output_written.append('%s.hx' % (fid % f))
    if 'cb' in otype or 'vmd' in otype and not print_waring:
      if is_vector: print_waring = True
      else: 
        display('\nSaving to .cb file...' +
                      '\n\t%(o)s.cb' % {'o': fid % f})
        cube_creator(d,(fid % f),geo_info,geo_spec,**kwargs)
        output_written.append('%s.cb' % (fid % f))
       #else: output_creator(d,(fid % f),geo_info,geo_spec)  # Axel's cube files
    if 'vmd' in otype and 'vmd' not in omit and not print_waring:
      if is_vector: print_waring = True
      else: 
        # Create VMD network 
        display('\nCreating VMD network file...' +
                      '\n\t%(o)s.vmd' % {'o': fid % f})        
        vmd_network_creator((fid % f),cube_files=['%s.cb' % (fid % f)])
        output_written.append('%s.vmd' % (fid % f))
      
  if print_waring:
    display('For a vectorized grid only HDF5 is available as output format...')
    display('Skipping all other formats...')
  
  return output_written
  # main_output 

def cube_creator(rho,filename,geo_info,geo_spec,comments='',**kwargs):
  '''Creates a plain text Gaussian cube file.
  '''
  
  # Open an empty file 
  fid = open('%(f)s.cb' % {'f': filename}, 'w')
  
  # Write the type and the position of the atoms in the header 
  string = 'orbkit calculation\n'
  string += ' %(f)s\n'  % {'f': comments}
  # How many atoms 
  string += ('%(at)d' % {'at': len(geo_info)}).rjust(5)
  # Minima
  for ii in range(3):
    string += ('%(min)0.6f' % {'min': grid.min_[ii]}).rjust(12)

  for ii in range(3):
    string += '\n'
    string += ('%(N)d' % {'N': grid.N_[ii]}).rjust(5)
    for jj in range(3):
      if jj == ii: 
        string += ('%(dr)0.6f' % {'dr': grid.delta_[ii]}).rjust(12)
      else:
        string += ('%(dr)0.6f' % {'dr': 0}).rjust(12)
  
  for ii in range(len(geo_info)):
    string += '\n'
    string += ('%(N)s' % {'N': geo_info[ii][2]}).rjust(5)
    string += ('%(ch)0.6f' % {'ch': float(geo_info[ii][1])}).rjust(12)
    for jj in range(3):
      string += ('%(r)0.6f' % {'r': geo_spec[ii][jj]}).rjust(12)
  string += '\n'
  for rr in range(len(grid.x)):
    for ss in range(len(grid.y)):
      for tt in range(len(grid.z)):
        string += ('%(rho).6E' % {'rho': rho[rr,ss,tt]}).rjust(13)
        if (tt % 6 == 5): 
          string += '\n'
      string += '\n'
  
  
  fid.write(string)
  
  # Close the file 
  fid.close()
  
  return 0
  # output_creator 
  
def pdb_creator(filename,qc,c_type='Lowdin'):
  aa_to_au = 1/0.52917720859
  fid = open(filename,'w')
  fid.write('HEADER    %s\n' % filename)
  fid.write('AUTHOR    orbkit\n') 
  string = ''
  for il in range(len(qc.geo_spec)):
    content = {'num': '%d'.rjust(6) % qc.geo_info[il][1],
               'type': qc.geo_info[il][0].rjust(3),
               'id': '1'.rjust(12)
              }
    string += 'ATOM  %(num)s%(type)s%(id)s    ' % content
    for i in reversed(range(3)):
      string += '%+.3f'.rjust(7)[:7] % (qc.geo_spec[il][i])/aa_to_au
    
    charge = 0 #if qc.pop_ana[c_type][il] == None else qc.pop_ana[c_type][il]
    string += '  1.00  %+.6f\n' % charge
  
  string += ('MASTER        0    0    0    0    0    0    0    0 ' + 
            '%s    0    0    0\nEND' % ('%s'.rjust(4) % len(qc.geo_spec)))
  fid.write(string)
  fid.close()

def xyz_creator(filename,qc,c_type='Lowdin'):
  aa_to_au = 1/0.52917720859
  fid = open(filename,'w')  
  if qc.etot == 0.:
    fid.write('%d\n\n' % len(qc.geo_spec))
  else:    
    fid.write('%d\n Energy = %22.15f E_h\n' % (len(qc.geo_spec),qc.etot))
  
  string = ''
  for il in range(len(qc.geo_spec)):
    string += '%-2s' % qc.geo_info[il][0]
    for i in range(3):
      string += ' %22.15f'  % (qc.geo_spec[il][i]/aa_to_au)
    
    if qc.pop_ana[c_type][il] is not None:
      string += ' %22.15f'  % qc.pop_ana[c_type][il]
    
    string += '\n'
    
  fid.write(string)
  fid.close()
  

def amira_creator(rho,filename):
  '''Creates a ZIBAmira mesh file. (plain text)
  '''
  # Open an empty file 
  fid = open('%(f)s.am' % {'f': filename},'w')

  # usage:
  #     - open Amira
  #     - left-click File -> Open Data
  #     - choose the sys.argv[2].am
  #     - Press OK
  #     - right-click on the new Data Object -> Compute -> Arithmetic
  #     - choose the Arithmetic object
  #     - select  Expr -> A and Result type -> regular and Apply
  #     - use the new data object to display your density as usual,
  
  # Write Header 
  fid.write('# AmiraMesh 3D ASCII 2.0\n\n\n')
  fid.write('define Lattice %(Nx)d %(Ny)d %(Nz)d\n' % 
                    {'Nx': grid.N_[0],'Ny': grid.N_[1],'Nz': grid.N_[2]})
  fid.write('define Coordinates %(N)d\n\n' % {'N': numpy.sum(grid.N_)})
  fid.write('Parameters {\n')
  fid.write('    Content "%(Nx)dx%(Ny)dx%(Nz)d float, uniform coordinates",\n' %
                    {'Nx': grid.N_[0],'Ny': grid.N_[1],'Nz': grid.N_[2]})
  fid.write('    BoundingBox %(xmin)f %(xmax)f %(ymin)f %(ymax)f %(zmin)f %(zmax)f,\n' %
            {'xmin': grid.min_[0],'xmax': grid.max_[0],
             'ymin': grid.min_[1],'ymax': grid.max_[1],
             'zmin': grid.min_[2],'zmax': grid.max_[2]})
  fid.write('    CoordType "uniform"\n}\n\n')
  fid.write('Lattice { float Data } @1\n')
  fid.write('# Data section follows\n@1\n')
  
  # Write density information to .am file
  string = ''
  for tt in range(len(grid.z)):
    for ss in range(len(grid.y)):
      for rr in range(len(grid.x)): 
        string += '%g\n' % rho[rr,ss,tt]
  
  fid.write(string)
  
  # Close the file 
  fid.close()
  
  return 0
  # amira_creator 


def amira_creator_vector(rho,filename):
  '''Creates a ZIBAmira mesh file using a rectingular grid.
  '''
  # Open an empty file 
  fid = open('%(f)s.am' % {'f': filename},'w')

  # usage:
  #     - open Amira
  #     - left-click File -> Open Data
  #     - choose the sys.argv[2].am
  #     - Press OK
  #     - right-click on the new Data Object -> Compute -> Arithmetic
  #     - choose the Arithmetic object
  #     - select  Expr -> A and Result type -> regular and Apply
  #     - use the new data object to display your density as usual,
  
  N = len(rho)
  
  # Write Header 
  fid.write('# AmiraMesh 3D ASCII 2.0\n\n\n')
  fid.write('define Lattice %(Nx)d %(Ny)d %(Nz)d\n' % 
            {'Nx': N,'Ny': N,'Nz': N})
  fid.write('define Coordinates %(N)d\n\n' % {'N': N})
  fid.write('Parameters {\n')
  fid.write('    Content "%(Nx)dx%(Ny)dx%(Nz)d float, rectilinear coordinates",\n' %
            {'Nx': N,'Ny': N,'Nz': N})
  fid.write('    CoordType "rectilinear"\n}\n\n')
  fid.write('Lattice { float Data } @1\n')
  fid.write('Coordinates { float xyz } @2\n\n')
  fid.write('# Data section follows\n@1\n')
  
  # Write density information to .am file
  string = ''
  #for tt in range(len(grid.z)):
    #for ss in range(len(grid.y)):
      #for rr in range(len(grid.x)): 
         #string += '%0.8f\n' % rho[rr,ss,tt]
  for ii in range(len(rho)):
    string += '%0.8f\n' % rho[ii]
  string += '\n@2\n'
  for xx in grid.x: 
    string += '%0.8f\n' % xx
  for yy in grid.y:  
    string += '%0.8f\n' % yy
  for zz in grid.z:  
    string += '%0.8f\n' % zz
  
  fid.write(string)
  
  # Close the file 
  fid.close()
  
  return 0
  # amira_creator_rectilinear_coord 

def amira_creator_rectilinear_coord(rho,filename):
  '''Creates a ZIBAmira mesh file using a rectilinear coordinates.
  '''
  
  # Open an empty file 
  fid = open('%(f)s.am' % {'f': filename},'w')

  # usage:
  #     - open Amira
  #     - left-click File -> Open Data
  #     - choose the sys.argv[2].am
  #     - Press OK
  #     - right-click on the new Data Object -> Compute -> Arithmetic
  #     - choose the Arithmetic object
  #     - select  Expr -> A and Result type -> regular and Apply
  #     - use the new data object to display your density as usual,
  
  # Write Header 
  fid.write('# AmiraMesh 3D ASCII 2.0\n\n\n')
  fid.write('define Lattice %(Nx)d %(Ny)d %(Nz)d\n' % 
            {'Nx': grid.N_[0],'Ny': grid.N_[1],'Nz': grid.N_[2]})
  fid.write('define Coordinates %(N)d\n\n' % {'N': numpy.sum(grid.N_)})
  fid.write('Parameters {\n')
  fid.write('    Content "%(Nx)dx%(Ny)dx%(Nz)d float, rectilinear coordinates",\n' %
            {'Nx': grid.N_[0],'Ny': grid.N_[1],'Nz': grid.N_[2]})
  fid.write('    CoordType "rectilinear"\n}\n\n')
  fid.write('Lattice { float Data } @1\n')
  fid.write('Coordinates { float xyz } @2\n\n')
  fid.write('# Data section follows\n@1\n')
  
  # Write density information to .am file
  string = ''
  for tt in range(len(grid.z)):
    for ss in range(len(grid.y)):
      for rr in range(len(grid.x)): 
        string += '%0.8f\n' % rho[rr,ss,tt]
  string += '\n@2\n'
  for xx in grid.x: 
    string += '%0.8f\n' % xx
  for yy in grid.y:  
    string += '%0.8f\n' % yy
  for zz in grid.z:  
    string += '%0.8f\n' % zz
  
  fid.write(string)
  
  # Close the file 
  fid.close()
  
  return 0
  # amira_creator_rectilinear_coord 

def hdf5_open(fid,mode='w'):
  '''Open an HDF5 file.'''
  import h5py
  HDF5_file = h5py.File(fid, mode)
  try:
    yield HDF5_file
  finally:
    HDF5_file.close()

def hdf5_append(x,group,name='data'):
  '''Automatically append data to a HDF5 file/group.'''
  if isinstance(x,numpy.ndarray):
    h5_dset = group.create_dataset(name,numpy.shape(x),data=x)
  elif isinstance(x,list):
    if name != '':
      subgroup = group.create_group(name)
    else:
      subgroup = group
    num = len(x)
    subgroup.attrs['num'] = num
    keys = range(num)
    #h5_dset = subgroup.create_dataset('keys',numpy.shape(keys),data=numpy.array(keys))
    for ii in keys:
      hdf5_append(x[ii],subgroup,name='%d' % ii)
  elif isinstance(x,dict):
    if name != '':
      subgroup = group.create_group(name)
    else:
      subgroup = group
    keys = x.keys()
    #h5_dset = subgroup.create_dataset('keys',numpy.shape(keys),data=numpy.array(keys))
    for ii in keys:
      hdf5_append(x[ii],subgroup,name=ii)
  else:
    group.attrs[name] = x
  return 0

def hdf52dict(group,HDF5_file):
  '''Automatically convert the data stored in an HDF5 file/group 
  to a python dictionary.
  '''
  try:
    # The selected group is a dataset 
    x = HDF5_file['%s' % group][()]
  except:
    # Read all members 
    members = list(HDF5_file['%(g)s' % {'g':group}])
    try:
      members = numpy.array(members, dtype = numpy.int64)
      x = []
      for mm in numpy.sort(members):
        x.append(hdf52dict('%(g)s/%(m)s' % {'g':group, 'm': mm},HDF5_file))
    except (ValueError,OverflowError):
      x = {}
      for mm in members:
        x[mm] = hdf52dict('%(g)s/%(m)s' % {'g':group, 'm': mm},HDF5_file)
      attrs = HDF5_file['%(g)s' % {'g':group}].attrs
      for ii_a in attrs:
        x[ii_a] = attrs[ii_a]
  return x

def hdf5_write(fid,mode='w',gname='',**kwargs):
  f = h5py.File(fid, mode)
  if gname is not '':
    group = f.create_group(gname)
    for i,j in kwargs.iteritems(): 
      group.create_dataset(i,numpy.shape(j),data=j)
  else:
    for i,j in kwargs.iteritems(): 
      f.create_dataset(i,numpy.shape(j),data=j)
  f.close()

def HDF5_creator(data,outputname,geo_info,geo_spec,data_id='rho',append=None,
            data_only=False,ao_spec=None,mo_spec=None,is_mo_output=False,
            x=None,y=None,z=None,**kwargs):
  '''Creates an HDF5 file (Hierarchical Data Format) output.
  '''
  import h5py
  
  if append is None:
    HDF5_file = h5py.File('%s.h5' % outputname, 'w')
    f = HDF5_file
  else:
    HDF5_file = h5py.File('%s.h5' % outputname, 'a')
    HDF5_file.require_group(append)
    f = HDF5_file[append]
  
  
  if is_mo_output:    
    mo_name = []
    for i,j in enumerate(data):
      try:
        mo_name.append(mo_spec[i]['sym'])
      except TypeError:
        mo_name.append(str(i))
      
      #dID = '%s:%s' % (data_id,mo_name[-1])
      #dset = f.create_dataset(dID,numpy.shape(j),data=j)
    
    dset = f.create_dataset('MO:Content',data=numpy.array(mo_name))
  
  if options.z_reduced_density:
    dset = f.create_dataset(data_id,numpy.shape(data),data=data)
  else:
    dset = f.create_dataset(data_id,numpy.shape(data),data=data)
  
  if data_only:
    HDF5_file.close()
    return 0
  
  if x is None: x = grid.x
  if y is None: y = grid.y
  if z is None: z = grid.z
  
  if options.z_reduced_density:
    dset = f.create_dataset('z',(1,len(z)),data=z)
  else:
    dset = f.create_dataset('x',(1,len(x)),data=x)
    dset = f.create_dataset('y',(1,len(y)),data=y)
    dset = f.create_dataset('z',(1,len(z)),data=z)
  
  if ao_spec is not None:
    hdf5_append(ao_spec,f,name='ao_spec')
    if mo_spec is not None:
      hdf5_append(mo_spec,f,name='mo_spec')
  if mo_spec is not None:
    MO_info = f.create_group('MO_info')
    occ_num=[]
    energy=[]
    sym=[]
    for ii in range(len(mo_spec)):
      occ_num.append(mo_spec[ii]['occ_num'])
      energy.append(mo_spec[ii]['energy'])
      sym.append(mo_spec[ii]['sym'])
    dset = MO_info.create_dataset('occ_num',((1,len(mo_spec))),data=occ_num)
    dset = MO_info.create_dataset('energy',((1,len(mo_spec))),data=energy)
    dset = MO_info.create_dataset('sym',((1,len(mo_spec))),data=sym)
  
  dset = f.create_dataset('geo_info',(numpy.shape(geo_info)),data=numpy.array(geo_info))
  dset = f.create_dataset('geo_spec',(numpy.shape(geo_spec)),data=geo_spec)
  
  HDF5_file.close()
  
  return 0
  # HDF5_creator 

def HDF5_creator_geo(filename,geo_info,geo_spec):
  '''Appends geo_info and geo_spec to an HDF5 file.'''
  import h5py
  fid = filename if filename.endswith('.h5') else '%s.h5' % filename
  f = h5py.File(fid, 'a')
  dset = f.create_dataset('geo_info',(numpy.shape(geo_info)),data=numpy.array(geo_info))
  dset = f.create_dataset('geo_spec',(numpy.shape(geo_spec)),data=geo_spec)
  f.close()
  
  return 0

def HDF5_creator_MO(MO,filename,geo_info,geo_spec,mo_spec):
  '''Creates an HDF5 file (Hierarchical Data Format) for MOs. (outdated)
  '''
  import h5py
  f = h5py.File(filename + '.h5', 'w')
  
  dset = f.create_dataset('x',(1,len(grid.x)),data=grid.x)
  dset = f.create_dataset('y',(1,len(grid.y)),data=grid.y)
  dset = f.create_dataset('z',(1,len(grid.z)),data=grid.z)
  
  mo_name = []
  for ij in range(len(MO)):
    mo_name.append(mo_spec[ij]['sym'])
    dID = 'MO:%s' % mo_spec[ij]['sym']
    
    dset = f.create_dataset(dID,((len(grid.x),len(grid.y),len(grid.z))),data=MO[ij])
  
  dset = f.create_dataset('MO:Content',data=numpy.array(mo_name))
  
  MO_info = f.create_group('MO_info')
  occ_num=[]
  energy=[]
  sym=[]
  for ii in range(len(mo_spec)):
    occ_num.append(mo_spec[ii]['occ_num'])
    energy.append(mo_spec[ii]['energy'])
    sym.append(mo_spec[ii]['sym'])
  dset = MO_info.create_dataset('occ_num',((1,len(mo_spec))),data=occ_num)
  dset = MO_info.create_dataset('energy',((1,len(mo_spec))),data=energy)
  dset = MO_info.create_dataset('sym',((1,len(mo_spec))),data=sym)
  
  dset = f.create_dataset('geo_info',(numpy.shape(geo_info)),data=numpy.array(geo_info))
  dset = f.create_dataset('geo_spec',(numpy.shape(geo_spec)),data=geo_spec)
  f.close()
  #mo_list = core.rho_compute(geo_spec,geo_info,ao_spec,mo_spec,calc_mo=True)
    
    #display('Writing %s ...' % fid)
    
    #f = h5py.File(fid, 'a')
    
    #for ii in range(len(mo_spec)):
      #dID = 'mo:%s' % mo_spec[ii]['sym']
      #f[dID][:,:,:] = mo_list[ii,:,:,:]
    
    #f.close()
  return 0
  # HDF5_creator 

def vmd_network_creator(filename,cube_files=None,render=False,iso=(-0.01,0.01),
                        abspath=True,**kwargs):
  from os import path,listdir
  from linecache import getline
  from orbkit import vmd_network_draft
  if cube_files is None:
    display('No list of cube (.cb) filenames provided. Checking the directory' + 
            ' of the outputfile...')
    cube_files = []
    for fid in listdir(path.dirname(filename)):
      if fid.endswith('.cb'):
        cube_files.append(fid)
    if cube_files == []:
      raise IOError('Could not find valid cube files in %s' % path.dirname(filename))
  
  title = []
  mo = ''
  for i,f in enumerate(cube_files):
    title = getline(f,2)
    if title.split() == []:
      title = path.splitext(path.basename(title))[0]
    else:
      title = title.replace('\n','').replace(' ','')
    pid = path.abspath(f) if abspath else path.relpath(f,path.relpath(filename))
    mo += vmd_network_draft.mo_string % {
                                  'c': i, 
                                  'n1': pid,
                                  'n2': title, 
                                  'isored': iso[0], 
                                  'isoblue': iso[1], 
                                  'render': '' if render else '#'
                                  }
  
  f = open('%(f)s.vmd' % {'f': filename},'w')
  f.write(vmd_network_draft.vmd_string % {'mo':mo})
  f.close()
  return 0
  # vmd_network_creator
  
def determine_rho_range(rho,start=0.01,stop=0.999):
  '''Get a range for the isosurface values.'''
  # Sort the density values 
  a=numpy.reshape(rho,-1)
  a=a[numpy.argsort(a)]
  
  # Where do we have the start and stop percentage? 
  n1=int(start*len(a))
  n2=int(stop*len(a))
  rho_min=a[n1]
  rho_max=a[n2]
  
  return rho_min, rho_max

def colormap_creator_peaks(filename,peaks,peak_width=0.02,peak_minus=None,peak_plus=None,alpha=0.2,rgb=0.2):  
  '''Creates a ZIBAmira colomap for selected data values.
  
  **Parameters:**
  
  filename : str
    Specifies the filename of the colormap.
  peaks : list
    Determines the values for peaks in the colormap.
  peak_width : float
    Specifies the width of of the peaks in the colormap.
  peak_min : None or float, optional
    Specifies the lower boundary of the colomap. (Peak with no hight.)
    If None, is set to the smallest data value minus 2*peak_width.
  peak_min : None or float, optional
    Specifies the upper boundary of the colomap. (Peak with no hight.)
    If None, is set to the larges data value plus 2*peak_width.
  alpha : float, data_range={0..1}
    Determines the opacity of the peak. (alpha = 1 - opacity)
  rgb : float or list or numpy.ndarray, data_range={0..1}
    If float or shape=(len(peaks),), specifies a the grey tone.
    Else, specifies the color in [red,green,blue].
  
  '''
  peaks = numpy.sort(peaks)
  if peak_minus is None:
    peak_minus = peaks[0]-(2*peak_width)
  if peak_plus is None:
    peak_plus = peaks[-1]+(2*peak_width)
  
  if isinstance(rgb,(float,int)):
    rgb = numpy.zeros((len(peaks),3)) + rgb
  else:
    rgb = numpy.array(rgb, dtype=float)
    if rgb.ndim == 1:
      if len(rgb) == 3:
        rgb = numpy.zeros((len(peaks),3)) + rgb[numpy.newaxis,:]
      elif len(rgb) == len(peaks):
        rgb = numpy.zeros((len(peaks),3)) + rgb[:,numpy.newaxis]
      else:
        raise ValueError("Wrong shape of 'rgb'")
    elif not (rgb.ndim == 2 and rgb.shape == (len(peaks),3)):
        raise ValueError("Wrong shape of 'rgb'")
  
  # Open a cmap file 
  fid = open('%(f)s.cmap' % {'f': filename}, 'w')
  
  # Write the header 
  fid.write('<!DOCTYPE Colormap>\n')
  fid.write('<ColormapVisage2.0 Name="%(f)s">\n' % {'f': filename})
  fid.write('  <Graph Active="1" Type="0" Name="">\n')
  
  # Initialize a counter for the contour values 
  counter = 0
  
  # Initialize a string for the contours 
  c_str = ('    <Control Opacity="%(o)f" Number="%(c)d" Blue="%(b)f"' + 
            ' Red="%(r)f" Green="%(g)f" Value="%(p)f"/>\n' )
  
  # Write the initial value at zero with zero opacity 
  fid.write(c_str % {'o': 0, 'c': counter, 'r': 0, 'g': 0, 'b': 0, 
                     'p': peak_minus})
  counter += 1
  
  for i,p in enumerate(peaks):
    print p
    # Write the peak 
    # Left edge of the peak
    fid.write(c_str % {'o': 0, 'c': counter, 'p': p-peak_width/2., 
                       'r': rgb[i,0], 'g': rgb[i,1], 'b': rgb[i,2]})
    counter += 1
    # The peak 
    fid.write(c_str % {'o': 1-alpha, 'c': counter, 'p': p, 
                       'r': rgb[i,0], 'g': rgb[i,1], 'b': rgb[i,2]})
    counter += 1
    # Right edge of the peak
    fid.write(c_str % {'o': 0, 'c': counter, 'p': p+peak_width/2., 
                       'r': rgb[i,0], 'g': rgb[i,1], 'b': rgb[i,2]})
    counter += 1
  
  # Write a final value at 1.5 * (final peak value) with zero opacity 
  fid.write(c_str % {'o': 0, 'c': counter, 'r': 0, 'g': 0, 'b': 0, 
                     'p': peak_plus})
  
  # Finalize the file 
  fid.write('  </Graph>\n')
  fid.write('</ColormapVisage2.0>')
  
  # Close the file
  fid.close()
  
  # colormap_creator 
    
  

def colormap_creator(rho,filename,n_peaks=5,start=0.01,stop=0.999,peak_width=0.1):
  '''Creates a .cmap colormap for ZIBAmira adjusted to the density.

  **Default:** Isosurface values between 1% and 99.9% of the total density.
  '''
  
  # Where do we have the start and stop percentage? 
  rho_min, rho_max = determine_rho_range(rho,start=start,stop=stop)
  
  # Compute the distance between two isosurface values 
  delta_peak =(rho_max-rho_min)/(n_peaks-1)
  
  # Open a cmap file 
  fid = open('%(f)s.cmap' % {'f': filename}, 'w')
  
  # Write the header 
  fid.write('<!DOCTYPE Colormap>\n')
  fid.write('<ColormapVisage2.0 Name="%(f)s">\n' % {'f': filename})
  fid.write('  <Graph Active="1" Type="0" Name="">\n')
  
  # Initialize a counter for the contour values 
  counter = 0
  
  # Initialize a string for the contours 
  c_str = ('    <Control Opacity="%(o)f" Number="%(c)d" Blue="%(v)f"' + 
            ' Red="%(v)f" Green="%(v)f" Value="%(p)f"/>\n' )
  
  # Write the initial value at zero with zero opacity 
  fid.write(c_str % {'o': 0, 'c': counter, 'v': 0, 'p': 0})
  counter += 1
  
  # Loop over the contour values 
  for ii in range(n_peaks):
    # Calculate the value for the isosurface peak and two values 
    # next to the peak with zero opacity 
    peak = rho_min+delta_peak*(ii+1)
    peak_minus = peak * (1 - peak_width/2.)
    peak_plus = peak * (1 + peak_width/2.)
    
    # Calculate a value for the opacity and the color
    value = 1-(float(ii+1)/(n_peaks+1)*0.9)
    
    # Write the peak 
    # Left edge of the peak 
    fid.write(c_str % {'o': 0, 'c': counter, 'v': value, 'p': peak_minus})
    counter += 1
    # The peak 
    fid.write(c_str % {'o': 1-value, 'c': counter, 'v': value, 'p': peak})
    counter += 1
    # Right edge of the peak 
    fid.write(c_str % {'o': 0, 'c': counter, 'v': value, 'p': peak_plus})
    counter += 1
  
  # Write a final value at 1.5 * (final peak value) with zero opacity 
  fid.write(c_str % {'o': 0, 'c': counter, 'v': 0, 'p': peak_plus*1.5})
  
  # Finalize the file 
  fid.write('  </Graph>\n')
  fid.write('</ColormapVisage2.0>')
  
  # Close the file
  fid.close()
  
  return 0
  # colormap_creator 

def hx_network_creator(rho,filename):
  '''Creates a ZIBAmira hx-network file including a colormap file (.cmap)
  adjusted to the density for the easy depiction of the density.
  '''
  from orbkit.hx_network_draft import hx_network
  # Create a .cmap colormap file using the default values 
  display('\tCreating ZIBAmira colormap file...\n\t\t%(f)s.cmap' % 
                {'f': filename})
  colormap_creator(rho,filename)
  
  # Create a .hx network file based on the file orbkit.hx_network_draft.py 
  display('\tCreating ZIBAmira network file...\n\t\t%(f)s.hx' % 
                {'f': filename})
  # Open an empty file
  fid = open('%(f)s.hx' % {'f': filename},'w')
  
  filename = filename.split('/')[-1]
  # Copy the content of the draft file and replace the keywords 
  fid.write(hx_network.replace("FILENAME",filename)) 
  
  # Close the file 
  fid.close()  
  
  return 0

def output_creator(rho,filename,geo_info,geo_spec):
  '''Creates a simple plain text output. (outdated)
  '''
  # Open an empty file 
  fid = open('%(f)s.cb' % {'f': filename}, 'w')
  
  # Write the type and the position of the atoms in the header 
  fid.write('Position of the nuclei (in a_0)\n')
  string = 'Number of nuclei:\t%d\n' % len(geo_info)
  for ii in range(len(geo_info)):
    for geo in geo_info[ii]:
      string += '%s\t' % geo
    for geo in geo_spec[ii]:
      string += '%0.8f\t' % geo
    string += '\n' 
  
  fid.write(string)
  
  # Write grid information for grid reconstruction
  fid.write('Grid data (in a_0)\n')
  fid.write(grid.grid_display(quiet=True,start=''))
  
  # Write density information
  fid.write('Data section begins (z runs fastest)  \n')
  
  string = ''
  for rr in range(len(grid.x)):
    for ss in range(len(grid.y)):
      for tt in range(len(grid.z)):
        string += '%+g\n' % rho[rr,ss,tt]
      string += '\n'
  
  fid.write(string)
  
  # Close the file 
  fid.close()
  
  return 0
  # output_creator 

# Class for the creation of a mo amira network 
#### NOT FINISHED YET ###
class cmo_display:
  def __init__(self):
    self.filename = options.outputname + '_mo'
    display("\tCreating ZIBAmira network file for \n\t  the depiction of the mos...\n\t\t" + self.filename + ".hx")    
    fid = open(self.filename + '.hx','w') 
    name = self.filename.split('/')[-1] 
    fid.close() 
    
  def colormap(self):
    display("\tCreating ZIBAmira colormap file for \n\t  the depiction of the mos...\n\t\t" + self.filename + ".hx")    
    fid = open(self.filename + '.col.am','w') 
    col_am = '''
# AmiraMesh 3D ASCII 2.0\n\n
define Lattice 4\n
Parameters {
    ContentType "Colormap",
    MinMax -50 50,
    Interpolate 0
}\n
Lattice { float[4] Data } @1\n
# Data section follows\n@1
1.000000000000000e+00 0.000000000000000e+00 0.000000000000000e+00 1.000000000000000e+00 
1.000000000000000e+00 0.000000000000000e+00 0.000000000000000e+00 1.000000000000000e+00 
0.000000000000000e+00 0.000000000000000e+00 1.000000000000000e+00 1.000000000000000e+00 
0.000000000000000e+00 0.000000000000000e+00 1.000000000000000e+00 1.000000000000000e+00 
    '''
    fid.write(col_am)
    fid.close()
#def hx_network_mo_diplay_creator
  ## Read line by line
  #counter = 0
  #factor=abs(float(flines[-1].split(" ")[0])-float(flines[0].split(" ")[0]))/100;
  #for ii, line in enumerate(flines):
    #counter += 1;
    #line = line.replace('\n', '')
    #column = line.split(" ")
    #if column[1] != str(0):
      #fid.write('    <Control Opacity="'+ str(0) + '" Number="'+ str(counter) + '" Blue="0" Red="0" Value="' + str(float(column[0])-factor) +'" Green="0"/>\n')
      #counter += 1;
      #fid.write('    <Control Opacity="'+ str(column[1]) + '" Number="'+ str(counter) + '" Blue="0" Red="0" Value="' + str(column[0]) +'" Green="0"/>\n')
      #counter += 1;
      #fid.write('    <Control Opacity="'+ str(0) + '" Number="'+ str(counter) + '" Blue="0" Red="0" Value="' + str(float(column[0])+factor) +'" Green="0"/>\n')
      #counter += 1;
    #else:
      #fid.write('    <Control Opacity="'+ str(column[1]) + '" Number="'+ str(counter) + '" Blue="0" Red="0" Value="' + str(column[0]) +'" Green="0"/>\n')

  #fid.write('  </Graph>\n')
  #fid.write('</ColormapVisage2.0>')

  #fid.close()


def h5am_creator(rho,filename):
  #  FUNCTION HDF5_creator  creates HDF5 file (Hierarchical Data Format) 
  import h5py

  #f = h5py.File(filename + '.h5am', 'w')
  
  with h5py.File(filename + '.h5am', 'w') as f:
    amira = f.create_group('amira')
    amira.attrs['version']     = 2
    amira.attrs['contenttype'] = 'HDF5amiralattice'
    amira.attrs['numdims']     = 3
    amira.attrs['dims']        = [len(grid.x),len(grid.y),len(grid.z)]  
    amira.attrs['boundingbox'] = [grid.x[0],grid.x[-1],grid.y[0],grid.y[-1],grid.z[0],grid.z[-1]]
    amira.attrs['latticetype'] = 'http://amira.zib.de/latticetypes#uniform'
    #amira.attrs['latticetype'] = 'http://amira.zib.de/latticetypes#rectilinear'
    #amira.attrs['coordX'] = grid.x
    #amira.attrs['coordY'] = grid.y  
    #amira.attrs['coordZ'] = grid.z
    amira.attrs['ndatasets'] = 1
  return
  
  if 0:
    dataset0 = amira.create_group('dataset:0')
    dataset0.attrs['ndatavar'] = 0
    dataset0.attrs['datatype'] = 'http://amira.zib.de/types#double'
    a = h5py.h5t.array_create(h5py.h5t.IEEE_F64LE, (len(grid.x),len(grid.y),len(grid.z)))
    dset = dataset0.create_dataset('timestep:0',(len(grid.x),len(grid.y),len(grid.z)),data=rho)#,dtype=numpy.float32)
  
  
  #print dset
  #dset = dataset0.create_dataset('timestep:0',(len(grid.x),len(grid.y),len(grid.z)),data=rho)
    
  #with h5py.File(filename + '.h5am', 'w') as f:
    #f['/amira/Attribute/contenttype'] = 'HDF5amiralattice';
    #f['/amira/Attribute/version'] = 2
    #f['/amira/Attribute/numdims'] = 3
    #f['/amira/Attribute/dims'] = [len(grid.x),len(grid.y),len(grid.z)]
    #f['/amira/Attribute/boundingbox'] = [grid.x[0],grid.x[-1],grid.y[0],grid.y[-1],grid.z[0],grid.z[-1]]
    #f['/amira/Attribute/latticetype'] = 'http://amira.zib.de/latticetypes#uniform'
    #f['/amira/Attribute/ndatasets'] = 1
    #f['/amira/Attribute/ndatavar'] = 1
    #f['/amira/Attribute/datatype'] = 'http://amira.zib.de/types#float'
    #f['/amira/dataset:0/timestep:0'] =rho

