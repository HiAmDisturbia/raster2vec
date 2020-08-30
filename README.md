# raster2vec
raster2vec is a plugin for QGIS, that transforms a raster image into a vector image, using the algorithms of L0 Cut-Pursuit and Potrace Multi-Labels. Credits goes to Hugo Raguet, aka 1a7r0ch3, who created these algorithms. They can be found here:

[Parallel Cut-Pursuit](https://gitlab.com/1a7r0ch3/parallel-cut-pursuit "Parallel Cut-Pursuit")

[Potrace Multi-Labels](https://gitlab.com/1a7r0ch3/multilabel-potrace "Potrace Multi-Labels")

I suggest you to install them, as they'll be used later on.

## How to install the plugin:
### Windows

Download the ZIP file of the entire raster2vec project. Extract the files from the zip file, copy the `raster2vec` folder, then paste it to:
`C:\Users\user_name\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`

`user_name` takes the name of your account on windows. As for `QGIS3`, if you are using another version of QGIS that is 2.X, the folder name would be QGIS2, but the paths would be the same.

After installing the plugin, we need the codes of both algorithms, in order to make the plugin work, and be read by QGIS. Download them in a ZIP file from the Gitlab links above.
Next, you extract the zip files, copy the folders `multilabel-potrace` and `parallel-cut-pursuit`, then paste them to the following path:
`C:\Users\user_name\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\raster2vec`

We have one more step to do, and we need to use the CMDOS for it. You can also use the Windows Powershell or a Prompt window, like Anaconda Prompt (if you're using Spyder).
So, in the interface, make sure you're in the correct path, using:
`cd C:\Users\user_name\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\raster2vec\multilabel-potrace\python`
`cd C:\Users\user_name\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\raster2vec\parallel-cut-pursuit\python`

Then, execute the following command:
`python setup.py build_ext`
This command will install the wrappers in the plugin, which will be read by QGIS.

Now the plugin should work, and be read by QGIS.

### Inside QGIS (works for both Windows and Linux)

This method is an easier way to install the plugin.
Download the ZIP file of the entire raster2vec project. Extract the files from the zip file, then create a ZIP file of the `raster2vec` folder.

Inside QGIS, go to Plugins -> Install plugins -> Install plugin from ZIP file. Then chose the zip file you just created. It'll automatically unzip it and place it to the correct filepath for you.

For the installation of the `multilabe-potrace` and `parallel-cut-pursuit` algorithms, you can follow the same steps as in the **Windows** paragraph.

### Credits

Plugin and code built by Paul-Alexandre Nasr
