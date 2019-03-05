
<style lang="css">
.parameter-file-editor {
  margin: 20px;
  min-height: 400px;
}
</style>
<template lang="html">
  <div class="parameter-file-editor" id="parameter-file-editor">
  </div>
</template>
<script>
export default {
  data() {
    return {
      aceEditor: null
    };
  },
  props: [
    'content'
  ],
  mounted() {
    this.init();
  },
  watch: {
    content(val, oldVal) {
      this.aceEditor.setValue(val, -1);
    }
  },
  methods: {
    init() {
      this.aceEditor = ace.edit("parameter-file-editor");
      this.aceEditor.setFontSize(18);
      // tEditor.setValue(this.fileTemplate, -1)
      // this.aceEditor.setValue("{name: 'ACE', value: 'file template'}", -1)
      if(this.content) {
        this.aceEditor.setValue(this.content, -1);
      }
    },
    getContent() {
      return this.aceEditor.getValue();
    }
  }
}
</script>
