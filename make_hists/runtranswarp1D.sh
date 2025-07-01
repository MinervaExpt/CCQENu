# export OUTHISTFILE=${CCQEMAT}/TransWarpOut_QElike_EAvail_20MeVneutblob_ME6Ap6_MnvTunev1_No2p2hTuneWarp.root
# export NOWARPFILE=${CCQEMAT}/EAvail_EAvailnonvtx_recoil_nowarp_tuneduntuned_20MeVneutblob_minervame6A_MnvTunev1_AntiNu_v15_warping_hep01_1.root
# export WARPFILE=${CCQEMAT}/EAvail_EAvailnonvtx_recoil_no2p2htunewarp_tuneduntuned_20MeVneutblob_minervame6A_MnvTunev1_AntiNu_v15_warping_hep01_1.root
# export WARPRECOHIST=h___QElike_warped___qelike___EAvail___reconstructed
# export WARPTRUEHIST=h___QElike_warped___qelike___EAvail___selected_truth
# export NOWARPRECOHIST=h___QElike___qelike___EAvail___reconstructed
# export NOWARPTRUEHIST=h___QElike___qelike___EAvail___selected_truth
# export MIGRATIONHIST=h___QElike___qelike___EAvail___response_migration

export OUTHISTFILE=${CCQEMAT}/TransWarpOut_QElike_EAvailNoNonVtxBlobs_ME6Ap_MnvTunev1_MnvTunev2warp.root
export NOWARPFILE=${CCQEMAT}/EAvail_EAvailnonvtx_recoil_nowarp_tuneduntuned_20MeVneutblob_minervame6A_MnvTunev1_AntiNu_v15_warping_hep01_1.root
export WARPFILE=${CCQEMAT}/EAvail_EAvailnonvtx_recoil_MnvTunev2warp_tuneduntuned_20MeVneutblob_minervame6A_MnvTunev2_AntiNu_v15_warping_hep01_1.root
export WARPRECOHIST=h___QElike___qelike___EAvailNoNonVtxBlobs___reconstructed
export WARPTRUEHIST=h___QElike___qelike___EAvailNoNonVtxBlobs___selected_truth
export NOWARPRECOHIST=h___QElike___qelike___EAvailNoNonVtxBlobs___reconstructed
export NOWARPTRUEHIST=h___QElike___qelike___EAvailNoNonVtxBlobs___selected_truth
export MIGRATIONHIST=h___QElike___qelike___EAvailNoNonVtxBlobs___response_migration

TransWarpExtraction --output_file ${OUTHISTFILE} --data ${WARPRECOHIST} --data_file ${WARPFILE} --data_truth ${WARPTRUEHIST} --data_truth_file ${WARPFILE} --migration ${MIGRATIONHIST} --migration_file ${NOWARPFILE} --reco ${NOWARPRECOHIST} --reco_file ${NOWARPFILE} --truth ${NOWARPTRUEHIST} --truth_file ${NOWARPFILE} --num_iter 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,40 --num_uni 1000 -C 2 -P 0.247524752


export OUTHISTFILE=${CCQEMAT}/TransWarpOut_QElike_EAvail_ME6Ap6_MnvTunev1_MnvTunev2warp.root
export NOWARPFILE=${CCQEMAT}/EAvail_EAvailnonvtx_recoil_nowarp_tuneduntuned_20MeVneutblob_minervame6A_MnvTunev1_AntiNu_v15_warping_hep01_1.root
export WARPFILE=${CCQEMAT}/EAvail_EAvailnonvtx_recoil_MnvTunev2warp_tuneduntuned_20MeVneutblob_minervame6A_MnvTunev2_AntiNu_v15_warping_hep01_1.root
export WARPRECOHIST=h___QElike___qelike___EAvail___reconstructed
export WARPTRUEHIST=h___QElike___qelike___EAvail___selected_truth
export NOWARPRECOHIST=h___QElike___qelike___EAvail___reconstructed
export NOWARPTRUEHIST=h___QElike___qelike___EAvail___selected_truth
export MIGRATIONHIST=h___QElike___qelike___EAvail___response_migration

TransWarpExtraction --output_file ${OUTHISTFILE} --data ${WARPRECOHIST} --data_file ${WARPFILE} --data_truth ${WARPTRUEHIST} --data_truth_file ${WARPFILE} --migration ${MIGRATIONHIST} --migration_file ${NOWARPFILE} --reco ${NOWARPRECOHIST} --reco_file ${NOWARPFILE} --truth ${NOWARPTRUEHIST} --truth_file ${NOWARPFILE} --num_iter 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,40 --num_uni 1000 -C 2 -P 0.247524752


export OUTHISTFILE=${CCQEMAT}/TransWarpOut_QElike_recoil_ME6Ap6_MnvTunev1_MnvTunev2warp.root
export NOWARPFILE=${CCQEMAT}/EAvail_EAvailnonvtx_recoil_nowarp_tuneduntuned_20MeVneutblob_minervame6A_MnvTunev1_AntiNu_v15_warping_hep01_1.root
export WARPFILE=${CCQEMAT}/EAvail_EAvailnonvtx_recoil_MnvTunev2warp_tuneduntuned_20MeVneutblob_minervame6A_MnvTunev2_AntiNu_v15_warping_hep01_1.root
export WARPRECOHIST=h___QElike___qelike___recoil___reconstructed
export WARPTRUEHIST=h___QElike___qelike___recoil___selected_truth
export NOWARPRECOHIST=h___QElike___qelike___recoil___reconstructed
export NOWARPTRUEHIST=h___QElike___qelike___recoil___selected_truth
export MIGRATIONHIST=h___QElike___qelike___recoil___response_migration

TransWarpExtraction --output_file ${OUTHISTFILE} --data ${WARPRECOHIST} --data_file ${WARPFILE} --data_truth ${WARPTRUEHIST} --data_truth_file ${WARPFILE} --migration ${MIGRATIONHIST} --migration_file ${NOWARPFILE} --reco ${NOWARPRECOHIST} --reco_file ${NOWARPFILE} --truth ${NOWARPTRUEHIST} --truth_file ${NOWARPFILE} --num_iter 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,40 --num_uni 1000 -C 2 -P 0.247524752