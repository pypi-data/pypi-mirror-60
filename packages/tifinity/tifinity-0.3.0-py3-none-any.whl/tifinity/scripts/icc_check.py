import argparse
import os
import numpy as np
import sys

from argparse import Namespace
from tifinity.modules import tiff_details
from tifinity.parser.tiff import Tiff
from tifinity.actions.icc_parser import IccProfile

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # Process CLI arguments #
    ap = argparse.ArgumentParser(prog="Tifinity ICC Checks",
                                 description="Checks that colour profiles have successfully migrated to JP2 files")

    ap.add_argument("tiffs", help="the TIFF file or folder containing TIFFs to check")
    #ap.add_argument("jp2s", )

    args = ap.parse_args()

    # load Adobe ICC Profile
    profiles = {}
    with open("C:/Users/pmay/Downloads/Adobe ICC Profiles (end-user)/RGB/AdobeRGB1998.icc", "rb") as f:
        profiles['AdobeRGB1998'] = np.fromfile(f, dtype="uint8")

    with open("C:/Users/pmay/Downloads/sRGB2014.icc", "rb") as f:
        profiles['sRGB2014'] = np.fromfile(f, dtype="uint8")

    with open("C:/Users/pmay/Downloads/sRGB_v4_ICC_preference.icc", "rb") as f:
        profiles['sRGB_v4'] = np.fromfile(f, dtype="uint8")

    if args.tiffs and os.path.isdir(args.tiffs):
        for root, dirs, files in os.walk(args.tiffs):
            for file in files:
                if not file.endswith(('.tif', '.tiff')):
                    continue
                # args = Namespace(tags=[256, 257, 262, 34675],
                #                  csv=True,
                #                  file=os.path.join(root, file))
                # tiff_details.module.process_cli(args)

                tiff = Tiff(os.path.join(root, file))

                matchadobe = False
                matchsRGB2014 = False
                matchsRGB_v4 = False
                tiff_icc_cs = None
                for ifd in tiff.ifds:
                    tiff_icc = ifd.get_tag_value(34675)
                    if tiff_icc is not None:
                        profile = IccProfile(tiff_icc)
                        tiff_icc_cs = profile.get_colour_space()

                        matchadobe = np.array_equal(tiff_icc, profiles['AdobeRGB1998'])
                        matchsRGB2014 = np.array_equal(tiff_icc, profiles['sRGB2014'])
                        matchsRGB_v4 = np.array_equal(tiff_icc, profiles['sRGB_v4'])

                        print ("[{0}],{1},{2},{3},{4}".format(file, tiff_icc_cs, matchadobe, matchsRGB2014, matchsRGB_v4))
                    else:
                        print ("[{0}],No ICC".format(file))



if __name__ == '__main__':
    main()