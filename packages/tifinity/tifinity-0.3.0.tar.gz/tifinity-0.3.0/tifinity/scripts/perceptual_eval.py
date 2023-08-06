import argparse
import os
import sys

from argparse import Namespace
from tifinity.parser.tiff import Tiff
from tifinity.modules.perceptual_validation import PerceptualValidation


comparisons = {
    ("C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/royal_ms_7_c_iv_f001r.tif",'AdobeRGB'):
        {
            ### Original file compared to original data (with no embedded ICC),
            ###  interpretted using different profiles
            "C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_no_embedded_profile.tif":
                [('AdobeRGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_AdobeRGB-AdobeRGB]"), # treats AdobeRGB data as AdobeRGB data
                 ('sRGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_AdobeRGB-sRGB]"),         # treats AdobeRGB data as sRGB data
                 #('RGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_AdobeRGB-RGB]")           # treats AdobeRGB data as RGB data
                ],

            ### Original file compared to original AdobeRGB data converted to RGB data (no embedded profile),
            ###  interpretted using different profiles
            "C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_conv_rgb.tif":
                [('AdobeRGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_RGB-AdobeRGB]"), # treats RGB data as AdobeRGB
                 ('sRGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_RGB-sRGB]"),         # treats RGB data as sRGB
                 #('RGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_RGB-AdobeRGB]")       # treats RGB data as RGB
                ],

            ### Original file compared to original AdobeRGB data converted to sRGB data (no embedded profile),
            ###  interpretted using different profiles
            "C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_conv_sRGB_no_embedded_profile.tif":
                [('AdobeRGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_sRGB-AdobeRGB]"),# treats sRGB data as AdobeRGB
                 ('sRGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_sRGB-AdobeRGB]"),    # treats sRGB data as sRGB
                 #('RGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_sRGB-AdobeRGB]")      # treats sRGB data as RGB
                ]
        },
    ("C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_conv_rgb.tif",'sRGB'):
        {
            ### Original file compared to original data (with no embedded ICC),
            ###  interpretted using different profiles
            "C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_conv_rgb_embedded.tif":
                [
                    ('AdobeRGB', "royal_ms_7_c_iv_f001r_IM_conv_rgb_[RGB-sRGB_vs_RGB-AdobeRGB]"),
                    ('sRGB', "royal_ms_7_c_iv_f001r_IM_conv_rgb_[RGB-sRGB_vs_RGB-sRGB]"),
                 #('RGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_AdobeRGB-RGB]")           # treats AdobeRGB data as RGB data
                ],
        }
}

comparisons2 = {
    ("C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_no_embedded_profile.tif",'sRGB'):
        {
            ### Original file compared to original data (with no embedded ICC),
            ###  interpretted using different profiles
            "C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_sRGB.tif":
                [('sRGB', "royal_ms_7_c_iv_f001r_IM_no_embedded_profile_[AdobeRGB-sRGB_vs_AdobeRGB-sRGB]"),
                 #('RGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_AdobeRGB-RGB]")           # treats AdobeRGB data as RGB data
                ],
        }
}

# comparisons2 = {
#     ("C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/royal_ms_7_c_iv_f001r.tif",'AdobeRGB'):
#         {
#             ### Original file compared to original data (with no embedded ICC),
#             ###  interpretted using different profiles
#             "C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_no_embedded_profile.tif":
#                 [#('AdobeRGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_AdobeRGB-AdobeRGB]"), # treats AdobeRGB data as AdobeRGB data
#                  ('sRGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_AdobeRGB-sRGB]"),         # treats AdobeRGB data as sRGB data
#                  #('RGB', "royal_ms_7_c_iv_f001r_[AdobeRGB-AdobeRGB_vs_AdobeRGB-RGB]")
#                 ],          # treats AdobeRGB data as RGB data
#         }
# }

###
   # [("C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/royal_ms_7_c_iv_f001r.tif", 'AdobeRGB'),             #1
   #  ("C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_sRGB.tif", 'sRGB'),      #4
   #  ("royal_ms_7_c_iv_f001r_[1_vs_4]", None)],
   #
   # [("C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/royal_ms_7_c_iv_f001r.tif", 'AdobeRGB'),             #1
   #  ("C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_conv_sRGB.tif", 'sRGB'), #5
   #  ("royal_ms_7_c_iv_f001r_[1_vs_5]", None)],
   #
   # [("C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/royal_ms_7_c_iv_f001r.tif", 'AdobeRGB'),             #1
   #  ("C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/IM/royal_ms_7_c_iv_f001r_IM_conv_sRGB_no_embedded_profile.tif", 'sRGB'),#6
   #  ("royal_ms_7_c_iv_f001r_[1_vs_6]", None)],

outdir = "C:/Data/DCW/IB_18/Tiffs/ColourProfileTests/output/"


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    limit = None

    comp_plan = comparisons

    for (tiff, t1_type) in comp_plan:
        # starting tiff and type
        t1 = Tiff(tiff)
        img1_lab = PerceptualValidation.convert_tiff_to_lab(t1, t1_type, limit)

        for tiff2 in comp_plan[(tiff, t1_type)]:
            # comparison tiff
            t2 = Tiff(tiff2)

            for (t2_type, compname) in comp_plan[(tiff, t1_type)][tiff2]:
                fname = outdir + compname

                img2_lab = PerceptualValidation.convert_tiff_to_lab(t2, t2_type, limit)
                distances = PerceptualValidation.calculate_distance(img1_lab, img2_lab, fname)
                PerceptualValidation.graph_distances(t1.ifds[0].get_image_width(), distances, fname)

if __name__ == '__main__':
    main()