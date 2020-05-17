import os.path, os, shutil

dir = 'distrib/source'

print('[[ Preparing Source Distribution for Reggie! ]]')
print('>> Destination directory: %s' % dir)

if os.path.isdir(dir): shutil.rmtree(dir)
os.makedirs(dir)

shutil.copytree('reggiedata', dir + '/reggiedata')
shutil.copytree('reggieextras', dir + '/reggieextras')
shutil.copy('license.txt', dir)
shutil.copy('readme.md', dir)
shutil.copy('reggie.py', dir)
shutil.copy('archive.py', dir)
shutil.copy('common.py', dir)
shutil.copy('lz77.py', dir)
shutil.copy('sprites.py', dir)
shutil.copy('build_release.py', dir)
shutil.copy('prepare_source_dist.py', dir)
