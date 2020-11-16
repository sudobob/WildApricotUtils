#!/usr/bin/env python3
import sys

# map spaceman signoff to wild apricot signoff

#
#     SPACEMAN SIGNOFF                                     ->    WILD APRICOT SIGNOFF
#
sm_to_wa_signoff_map ={
"[equipment] *GREEN"                                        : "[signoff] GREEN ORIENTATION",
"[equipment] *Minor or Supervised Access Only"              : "[category] *Minor or Supervised Access Only",
"[equipment] *Minor over 16"                                : "[category] *Minor over 16",
"[equipment] *Minor under 16"                               : "[category] *Minor under 16",
"[equipment] 3D_HP 3D Scanner"                              : "[equipment] 3D_HP 3D Scanner",
"[equipment] 3D_Printers"                                   : "[equipment] 3D_Printers",
"[equipment] AC_APW_Heat Transfer Press"                    : "[equipment] AC_APW_Heat Transfer Press",
"[equipment] AC_Consew_Red Sewing Machine"                  : "[equipment] AC_Consew_Red Sewing Machine",
"[equipment] AC_Happy_Embroidery Machine"                   : "[equipment] AC_Happy_Embroidery Machine",
"[equipment] AC_NA_Embroidery Machine Safety"               : "[equipment] AC_NA_Embroidery Machine Safety",
"[equipment] AC_NA_Stained Glass Safety"                    : "[equipment] AC_NA_Stained Glass Safety",
"[equipment] AC_PFAFF_Embroidery Machine*"                  : "[equipment] AC_PFAFF_Embroidery Machine*",
"[equipment] AC_Silhouette_Electronic Cutter"               : "[equipment] AC_Silhouette_Electronic Cutter",
"[equipment] AC_Ultramatic_Embroidery Machine"              : "[equipment] AC_Ultramatic_Embroidery Machine",
"[equipment] AC_USCutter_Vinyl Cutter"                      : "[equipment] AC_USCutter_Vinyl Cutter",
"[equipment] AC_various_Jewelry Soldering Equipment Safety" : "[equipment] AC_various_Jewelry Soldering Equipment Safety",
"[equipment] BL_Blacksmithing Safety"                       : "[equipment] BL_Blacksmithing Safety",
"[equipment] BL_Blacksmithing Setup"                        : "[equipment] BL_Blacksmithing Setup",
"[equipment] BL_Coal Ironworks_Hydraulic Forging Press*"    : "[equipment] BL_Coal Ironworks_Hydraulic Forging Press*",
"[equipment] BL_Origin Blade Maker_72in Belt Grinder"       : "[equipment] BL_Origin Blade Maker_72in Belt Grinder",
"[equipment] BL_Rigid_Abrasive_Chopsaw"                     : "[equipment] BL_Rigid_Abrasive_Chopsaw",
"[equipment] CC_ShopSabre_Safety"                           : "[equipment] CC_ShopSabre_Safety",
"[equipment] CS_Fritzinger_Rotocaster"                      : "[equipment] CS_Fritzinger_Rotocaster",
"[equipment] CS_Kervina_Thermoformer"                       : "[equipment] CS_Kervina_Thermoformer",
"[equipment] EL_Reflow Station Safety*"                     : "[equipment] EL_Reflow Station Safety*",
"[equipment] EL_Yellow Safety"                              : "[equipment] EL_Yellow Safety",
"[equipment] LC_NA_Roller Rotary tool"                      : "[equipment] LC_NA_Roller Rotary tool",
"[equipment] MW_Everlast_Plasma Cutter*"                    : "[equipment] MW_Everlast_Plasma Cutter*",
"[equipment] MW_Everlast_TIG Welder"                        : "[equipment] MW_Everlast_TIG Welder",
"[equipment] MW_Grizzly_Cold Cut Saw"                       : "[equipment] MW_Grizzly_Cold Cut Saw",
"[equipment] MW_Matsuura Tiger_CNC Mill"                    : "[equipment] MW_Matsuura Tiger_CNC Mill",
"[equipment] MW_Miller_MIG Welder"                          : "[equipment] MW_Miller_MIG Welder",
"[equipment] MWS_Central Forge_Throatless Shear"            : "[equipment] MWS_Central Forge_Throatless Shear",
"[equipment] MWS_Chicago Electric_Spot Welder"              : "[equipment] MWS_Chicago Electric_Spot Welder",
"[equipment] MWS_Woodward Fab_Sheet Metal Brake"            : "[equipment] MWS_Woodward Fab_Sheet Metal Brake",
"[equipment] MWS_Woodward Fab_Sheet Metal Shear"            : "[equipment] MWS_Woodward Fab_Sheet Metal Shear",
"[equipment] MWY__Yellow Safety"                            : "[equipment] MWY__Yellow Safety",
"[equipment] MWY_Central Forge_Pneumatic Media Blaster"     : "[equipment] MWY_Central Forge_Pneumatic Media Blaster",
"[equipment] MWY_Central Machinery_1x30 Belt Sander"        : "[equipment] MWY_Central Machinery_1x30 Belt Sander",
"[equipment] MWY_Delta_Bench Grinder"                       : "[equipment] MWY_Delta_Bench Grinder",
"[equipment] MWY_Grizzly_Horizontal Bandsaw"                : "[equipment] MWY_Grizzly_Horizontal Bandsaw",
"[equipment] MWY_Grizzly_Vertical Bandsaw"                  : "[equipment] MWY_Grizzly_Vertical Bandsaw",
"[equipment] MWY_Milwaukee_Portaband"                       : "[equipment] MWY_Milwaukee_Portaband",
"[equipment] MWY_Northern Industrial_Drill Press"           : "[equipment] MWY_Northern Industrial_Drill Press",
"[equipment] MWY_Various_Angle Grinders"                    : "[equipment] MWY_Various_Angle Grinders",
"[equipment] SL_FormLabs_SLA Printer"                       : "[equipment] SL_FormLabs_SLA Printer",
"[equipment] WW_Bandsaw_Safety"                             : "[equipment] WW_Bandsaw_Safety",
"[equipment] WW_General_Bandsaw Red"                        : "[equipment] WW_General_Bandsaw Red",
"[equipment] WW_Jet_Thickness Sander"                       : "[equipment] WW_Jet_Thickness Sander",
"[equipment] WW_Rikon_Bandsaw Red"                          : "[equipment] WW_Rikon_Bandsaw Red",
"[equipment] WW_Various_Router_Safety"                      : "[equipment] WW_Various_Router_Safety",
"[equipment] WW_Various_Routers"                            : "[equipment] WW_Various_Routers",
"[equipment] WWL_Delta_Lathe"                               : "[equipment] WWL_Delta_Lathe",
"[equipment] WWL_Jet_Lathe"                                 : "[equipment] WWL_Jet_Lathe",
"[equipment] WWL_Nova Galaxy_Lathe"                         : "[equipment] WWL_Nova Galaxy_Lathe",
"[equipment] WWR__Red Safety"                               : "[equipment] WWR__Red Safety",
"[equipment] WWR_Delta_Planer"                              : "[equipment] WWR_Delta_Planer",
"[equipment] WWR_Dewalt_Sliding miter saw"                  : "[equipment] WWR_Dewalt_Sliding miter saw",
"[equipment] WWR_Hitachi_Miter Saw"                         : "[equipment] WWR_Hitachi_Miter Saw",
"[equipment] WWR_Laguna_Jointer"                            : "[equipment] WWR_Laguna_Jointer",
"[equipment] WWR_SawStop_Table Saw"                         : "[equipment] WWR_SawStop_Table Saw",
"[equipment] WWY__Yellow Safety"                            : "[equipment] WWY__Yellow Safety",
"[equipment] WWY_Delta_Disk_Or_Belt_Sander"                 : "[equipment] WWY_Delta_Disk_Or_Belt_Sander",
"[equipment] WWY_Delta_Spindle or Oscillating Sander"       : "[equipment] WWY_Delta_Spindle or Oscillating Sander",
"[equipment] WWY_Dewalt_Scroll Saw"                         : "[equipment] WWY_Dewalt_Scroll Saw",
"[equipment] WWY_Grizzly_Bandsaw"                           : "[equipment] WWY_Grizzly_Bandsaw",
"[equipment] WWY_Powermatic_Hollow Chisel Mortiser"         : "[equipment] WWY_Powermatic_Hollow Chisel Mortiser",
"[equipment] WWY_Various_Drill Press"                       : "[equipment] WWY_Various_Drill Press",
"[novapass] CC_ShopSabre_CNC Router"                        : "[novapass] CC_ShopSabre_CNC Router",
"[novapass] LC_Hurricane_Laser Cutter"                      : "[novapass] LC_Hurricane_Laser Cutter",
"[novapass] LC_Rabbit_Laser Cutter"                         : "[novapass] LC_Rabbit_Laser Cutter",
"[novapass] MW_Enco_Metal Lathe"                            : "[novapass] MW_Enco_Metal Lathe",
"[novapass] MW_Enco_Vertical Mill"                          : "[novapass] MW_Enco_Vertical Mill",
"[novapass] SL_FormLabs_SLA Printer"                        : "[novapass] SL_FormLabs_SLA Printer",
"[novapass] WWR_Dewalt_Sliding miter saw"                   : "[novapass] WWR_Dewalt_Sliding miter saw",
"[novapass] WWR_SawStop_Table Saw"                          : "[novapass] WWR_SawStop_Table Saw",
"accounting"                                                : "[category] accounting",
"admins"                                                    : "[category] admins",
"associates"                                                : "[category] associates",
"blogadmins"                                                : "[category] blogadmins",
"cmsusers"                                                  : "[category] cmsusers",
"dbadmins"                                                  : "[category] dbadmins",
"directors"                                                 : "[category] directors",
"facilities"                                                : "[category] facilities",
"founders"                                                  : "[category] founders",
"members"                                                   : "[category] members",
"officers"                                                  : "[category] officers",
"operations"                                                : "[category] operations",
"waiver"                                                    : "[category] waiver",
"wikiadmins"                                                : "[category] wikiadmins"
}

def process(raw_signoffs_from_spaceman):
    """
    input: an signoff entry from  spaceman like:

    '[equipment]-LC_Hurricane_Laser-Cutter:[equipment]-*GREEN:[equipment]-LC_Rabbit_Laser-Cutter:[novapass]-LC_Hurricane_Laser-Cutter:[equipment]-3D_Printers:[novapass]-LC_Rabbit_Laser-Cutter'

    this is broken down into individual signoffs

    '[equipment] LC_Hurricane_Laser Cutter'
    '[equipment] *GREEN:[equipment] LC_Rabbit_Laser Cutter'
    '[novapass] LC_Hurricane_Laser Cutter'

    output:

    a list of corresponding signoffs in WA

    ['*GREEN', '[novapass] LC_Hurricane_Laser Cutter', '[equipment] 3D_Printers', '[novapass] LC_Rabbit_Laser Cutter']


    """

    found_signoffs = []
    signoffs_from_spaceman = raw_signoffs_from_spaceman.split(':')
    for sm_indiv_signoff  in signoffs_from_spaceman:
        sm_indiv_signoff = sm_indiv_signoff.replace('-',' ')
        #sys.stdout.write(f'{sm_indiv_signoff:<64} : ') 
        if sm_indiv_signoff in sm_to_wa_signoff_map:
            found_signoffs.append(sm_to_wa_signoff_map[sm_indiv_signoff])
            #sys.stdout.write(f'{ sm_to_wa_signoff_map[sm_indiv_signoff]:<64}\n')
        #else:
            #sys.stdout.write(f'<not found>\n')

    return found_signoffs

if __name__ == '__main__':
    pass
