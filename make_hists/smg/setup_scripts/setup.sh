PLACE1='WorkComputer' # local
PLACE2='minerva'      # minervagpvm0#.fnal.gov
PLACE3='hep01'        # hep01.physics.oregonstate.edu

# Set WHEREIPUTMYCODE based on machine 
if [[ "$HOSTNAME" == *"$PLACE1"* ]]; then
	cd $HOME/MinervaExpt/CCQENu/make_hists/smg
	source setup_scripts/local.sh
	
elif [[ "$HOSTNAME" == *"$PLACE2"* ]]; then
	cd /minerva/app/users/$USER/minerva/CCQENu/make_hists/smg
	source setup_scripts/mnv.sh
	
elif [[ "$HOSTNAME" == *"$PLACE3"* ]]; then
	cd $HOME/MinervaExpt/CCQENu/make_hists/smg
	source setup_scripts/hep01.sh
	
else
	echo -e "\n \$HOSTNAME does not contain any assigned \$PLACE#."
	echo -e " Please update this setup script for your environment.\n"
		
fi

if [[ -d "playlist" ]]; then
	rm playlist
fi
ln -s $PLAYLISTDIR playlists
