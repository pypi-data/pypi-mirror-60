import muDIC as dic
import logging
import numpy as np
from copy import deepcopy

# Set the amount of info printed to terminal during analysis
logging.basicConfig(format='%(name)s:%(levelname)s:%(message)s', level=logging.INFO)

# Path to folder containing images
path = r'./meat/'  # Use this formatting on Linux and Mac OS
# path = r'c:\path\to\example_data\\'  # Use this formatting on Windows

# Generate image instance containing all images found in the folder
images = dic.IO.image_stack_from_folder(path, file_type='.tiff')
# images.set_filter(dic.filtering.lowpass_gaussian, sigma=1.)
# images.skip_images([0])


# Generate mesh
mesher = dic.Mesher(deg_e=3, deg_n=3)
mesh_prerun = mesher.mesh(images, Xc1=493, Xc2=911, Yc1=314, Yc2=762, n_ely=4, n_elx=4, GUI=False)

# Instantiate settings object and set some settings manually
settings = dic.DICInput(mesh_prerun, images)
settings.maxit = 100
settings.tol = 1e-5
settings.noconvergence = "ignore"

# Instantiate job object
job = dic.DICAnalysis(settings)

# Running DIC analysis
dic_results_prerun = job.run()

mesh_fine = deepcopy(mesh_prerun)
mesh_fine.n_elx = 13
mesh_fine.n_ely = 13
mesh_fine.gen_node_positions()

intial_xs, inital_ys = dic.mesh.mesh_translator(mesh_prerun, mesh_fine, dic_results_prerun)

# Instantiate settings object and set some settings manually
# images.set_filter(lambda x:x)
settings = dic.DICInput(mesh_fine, images)
settings.ref_update = [3]
settings.maxit = 100
settings.noconvergence = "ignore"
settings.node_hist = [intial_xs[:, :3], inital_ys[:, :3]]
# If you want to access the residual fields after the analysis, this should be set to True

# Instantiate job object
job = dic.DICAnalysis(settings)
dic_results = job.run()

# Calculate field values
fields = dic.post.viz.Fields(dic_results, seed=51)

# Show a field
viz = dic.Visualizer(fields, images=images)

# Uncomment the line below to see the results
# viz.show(field="true strain", component = (1,1), frame = 39)

#import matplotlib.pyplot as plt
#
#plt.ion()
#
#save_variables = ["displacement", "truestrain"]
#save_components = [(0, 0), (1, 1)]
#for variable in save_variables:
#    for component in save_components:
#        for i in range(dic_results.xnodesT.shape[1]):
#            viz.show(field=variable, component=component, frame=i)
#            plt.savefig("results/%s_%s%i.png" % (variable, str(component), i))
#            plt.close()
#
#strain = fields.true_strain()
#plt.plot(strain[0, 1, 1, 25, 25, :], '-*', label="eps_yy in centre")
#plt.plot(np.average(strain[0, 1, 1, :, 25, :], axis=0), '-*', label="eps_yy horizontal average")
#plt.plot(strain[0, 0, 0, 25, 25, :], '-*', label="eps_xx in centre")
#plt.plot(np.average(strain[0, 0, 0, :, 25, :], axis=0), '-*', label="eps_xx vertical average")
#plt.ylim(ymin=0)
#plt.xlim(xmin=0)
#plt.xlabel("Frame id [-]")
#plt.ylabel("True strain [-]")
#plt.legend(frameon=False)
#plt.savefig("results/strains.pdf")
#plt.close()
