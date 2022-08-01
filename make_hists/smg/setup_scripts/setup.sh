PLACE1='WorkComputer' # local
PLACE2='minerva'      # minervagpvm0#.fnal.gov
PLACE3='hep01'        # hep01.physics.oregonstate.edu

# Set WHEREIPUTMYCODE based on machine 
if [[ "$HOSTNAME" == *"$PLACE1"* ]]; then
	source $HOME/MinervaExpt/CCQENu/make_hists/smg/setup_scripts/local.sh
	cd $CCQEMAT/smg
	
elif [[ "$HOSTNAME" == *"$PLACE2"* ]]; then
	source /minerva/app/users/$USER/minerva/CCQENu/make_hists/smg/setup_scripts/mnv.sh
	cd $CCQEMAT/smg
	
elif [[ "$HOSTNAME" == *"$PLACE3"* ]]; then
	source $HOME/MinervaExpt/CCQENu/make_hists/smg/setup_scripts/hep01.sh
	cd $CCQEMAT/smg
	
else
	echo -e "\n \$HOSTNAME does not contain any assigned \$PLACE#."
	echo -e " Please update this setup script for your environment.\n"
		
fi

ln -s $PLAYLISTDIR playlist
echo -e "\n'playlist' points to "$PLAYLISTDIR"\n"
