import sys

from jbase.replace import Replace

spr_range = range(3981, 4000)
blend_range = range(19)

item = Replace(src='ground_temperate_grass.blend',
               frames={key: val for (key, val) in zip(spr_range, blend_range)}
               )
