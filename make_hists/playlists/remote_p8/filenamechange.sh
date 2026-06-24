for x in *"P8_Playlist"*; do
  mv -- "$x" "${x//P8_Playlist/minervame}"
done

