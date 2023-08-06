# ev3devlogging 

When writing a program it can be convenient to log what the program is doing. After executing the 
program you can then easily analyse what really happened.

Normally people use 'print' calls, but when running the program on the EV3 these are difficult to
read on its small screen. It is more convenient to use a logging library which writes your log messages 
to a file. The 'ev3devlogging' library gives you only the two basic functions:

* log(msg)       :  writes the message 'msg' to the log
* timedlog(msg)  :  writes the message 'msg' to the log prepended with the time of the log


Note: python has standard logging library, however configure such a logging library is somewhat 
technical. To keep things easy we  made the 'ev3devlogging' library which uses
the standard logging library to give you a very a basic usage API. 

## Example 

example 1: using both log and timedlog 

    from ev3devlogger import log
    from ev3devlogger import timedlog
    
    log("my first log message")
    timedlog("my first timed log message")
    
    log("my second log message")

example 2: using timedlog as log

    from ev3devlogger import timedlog as log
    log("my first timed log message")


For more examples see: https://github.com/ev3dev-python-tools/thonny-ev3dev/wiki/

## Log file on EV3

When a program is running on the EV3 and an error happens or any logging information is generated,
then a so called ’.err.log’ file gets created on the EV3 where all error and log messages are stored.

After your program is done, you can retreive this '.err.log' file from the EV3 to analyse
the execution of the program. You can then use some low level ssh/sftp/scp commands to 
retreive the logfile. However there are two tools which makes it easier for you:

* The 'ev3devcmd' package gives you an easy 'ev3dev' command which makes
it easy to retreive this log file. It does all the ssh commands for you. 
* The Thonny IDE has athonny-ev3dev plugin which integrates the ev3devcmd package within the IDE. This allows you with a
press of a button to retreive the log file, and view in the IDE.
 
## Installing ev3devlogging library on the EV3

By default the 'ev3devlogging' library is not installed on the ev3dev operating system.
There are two easy ways to install this libary.

Using the 'ev3dev' commandline tool:

     ev3dev install_logging 
     
Or using the Thonny IDE with the thonny-ev3dev plugin installed. From within  Thonny  
give the following menu command:

      Menu "Device" -> choose menu item "Install ev3devlogging to the EV3"
    

     
 Both methods assume you have connected the EV3 with an USB cable to your pc, and the EV3 is
 set in usb-tethering mode.    
