function _templateNametag(tag) {
    return `<span class="badge badge-primary badge-tags">${_.escape(tag.slice(5))}</span>`;
}

function nametagTemplate(historyItem) {
    let uniqueNametags = _.filter(_.uniq(historyItem.tags), t => t.indexOf("name:") === 0);
    let nametagsDisplay = _.sortBy(uniqueNametags).map(_templateNametag);
    return `
        <div class="nametags" title="${uniqueNametags.length} nametags">
            ${nametagsDisplay.join("")}
        </div>`;
}

export default {
    nametagTemplate: nametagTemplate
};
