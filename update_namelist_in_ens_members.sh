
for idir in 'ctrlAE_04/' 'expAE02_04' 'expAE03_04' 'expAE04_04' 'expAE05_04' 'expAE11_04' 'expAE12_04' 'expAE13_04' 'expAE14_04' ;
 do
   sed -i 's/^.*config_adaptive_timestep_CFL_fraction.*/   config_adaptive_timestep_CFL_fraction = 0.5/' $idir/namelist.landice
 done
