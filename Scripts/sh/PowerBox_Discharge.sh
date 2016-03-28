#!/bin/sh

### BEGIN INIT INFO
# Provides:				PowerBox_Discharge
# Required-Start:		$remote_fs $syslog
# Required-Stop:		$remote_fs $syslog
# Default-Start:		2 3 4 5
# Default-Stop: 		0 1 6
# Short-Description:	Characterizes the PowerBox using the oscilloscope for voltage measurements and the lock-in amplifier for noise measurements.
# Description:			Characterizes the PowerBox using the oscilloscope for voltage measurements and the lock-in amplifier for noise measurements.
### END INIT INFO

DIR=/usr/local/bin/PowerBox_Characterization
DAEMON=$DIR/PowerBox_Discharge.py
DAEMON_NAME=PowerBox_Discharge

# arguments
DAEMON_OPTS="--service --log /var/log/PowerBox_Discharge.log"

# root is needed to utilize usbtmc and speak with the oscilloscope
DAEMON_USER=root

# Where the process ID is being stored
PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

do_start ()
{
	log_daemon_msg "Starting system $DAEMON_NAME daemon"
	start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON -- $DAEMON_OPTS
	log_end_msg $?
}
do_stop ()
{
	log_daemon_msg "Stopping system $DAEMON_NAME daemon"
	start-stop-daemon --stop --pidfile $PIDFILE --retry=TERM/30/KILL/5
	log_end_msg $?
}

case "$1" in
	start|stop)
		do_${1}
		;;
	restart|reload|force-reload)
		do_stop
		do_start
		;;
	status)
		status_of_proc "$DAEMON_NAME" "$DAEMON" && (exit 0 || $?)
		;;
	*)
		echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status}"
		exit 1
		;;
esac

exit 0
