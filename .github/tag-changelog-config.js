module.exports = {
  types: [
    { types: ["other"], label: "Commits" },
  ],

  renderTypeSection: function (label, commits) {
    let text = `\n## ${label}\n`;

    commits.forEach((commit) => {
      text += `- ${commit.subject}\n`;
    });

    return text;
  },

  renderChangelog: function (release, changes) {
    const now = new Date();
    return `# ${release} - ${now.toISOString().substr(0, 10)}\n` + changes + "\n\n";
  },
};
