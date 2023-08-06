# coding: utf-8
#! python3  # noqa: E265

"""
    Matching table between FME and Isogeo geometry names.
"""

MATCHER_GEOMETRY = {
    "fme_point": "Point",
    "fme_area": "Polygon",
    "fme_line": "LineString",
    "fme_arc": "Curve",
    "fme_collection": "GeometryCollection",
    "fme_ellipse": "Curve",
    "fme_surface": "Surface",
    "fme_point_cloud": "Point",
}


# #############################################################################
# ##### Main #######################
# ##################################
if __name__ == "__main__":
    pass
