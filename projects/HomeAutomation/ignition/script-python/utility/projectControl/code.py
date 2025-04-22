projectVersion = "7_0_0"
srcProjFileFolder = "c:\Program Files\Inductive Automation\Ignition\data\projects"
logger = system.util.getLogger('projectControl')
def getProjectVersion():
	return projectVersion
	
def exportProject():
	return

def importProject():
	return

def moveProjectFiles(project, dstFolder):
	import shutil
	import os
	src_dir = srcProjFileFolder + '\\' + project
	dst_dir = dstFolder + '\\' + project
	logger.info("src_dir: %s, dst_dir: %s"%(src_dir, dst_dir))
	
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	for item in os.listdir(src_dir):
	    src_path = os.path.join(src_dir, item)
	    dst_path = os.path.join(dst_dir, item)
	
	    if os.path.isdir(src_path):
	        if not os.path.exists(dst_path):
	            shutil.copytree(src_path, dst_path)
	        else:
	            shutil.rmtree(dst_path)
	            shutil.copytree(src_path, dst_path)
	    else:
	        shutil.copy2(src_path, dst_path)
	res = 'project %s moved from %s to %s -- COMPLETE'%(project, src_dir, dst_dir)
	return res