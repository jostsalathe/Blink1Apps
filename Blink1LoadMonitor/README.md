Blink1LoadMonitor
===

This is a little program that can run in the background and displays the system load in color intensity.

The following LED.color to value mapping is utilized:
 - 1.red = network transmission (all networks)
 - 1.green = network reception (all networks)
 - 1.blue = CPU utilization
 - 2.red = disk writes (all disks)
 - 2.green = disk reads (all disks)
 - 2.blue = memory utilization

A sample Windows task is included that runs the program automatically on startup. 
