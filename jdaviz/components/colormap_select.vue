<template>
  <v-select
    attach
    :menu-props="{ left: true }"
    :items="image_colormap_sync.choices"
    v-model="image_colormap_value"
    label="Colormap"
    dense
  >
    <template v-slot:selection="{ item, index }">
      <span>{{ item.text }}</span>
    </template>
    <template v-slot:item="{ item }">
      <span class="pr-6">{{ item.text }}</span>
      <v-card :style=colorStyle(item, cmap_samples) class="ps-6">.</v-card>
    </template>
  </v-select>
</template>

<script>
module.exports = {
  props: ['items', 'cmap_samples', 'image_colormap_sync', 'image_colormap_value'],
  methods: {
    colorStyle(item, cmap_samples) {
      var cmap_strip_width = 1
      var colors = []
      var style = 'repeating-linear-gradient( 135deg, '

      colors = cmap_samples[item.text]

      cmap_strip_width = strip_width / colors.length
      for ([ci, color] of colors.entries()) {
        var start = mi*strip_width + ci*cmap_strip_width
        var end = mi*strip_width+(ci+1)*cmap_strip_width
        style += color + ' '+start+'px, ' + color + ' '+end+'px'
        if (ci !== colors.length-1) {
          style += ', '
        }
      }

      style += ')'
      return style
    }
  }
};
</script>