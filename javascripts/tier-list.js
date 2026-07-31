(function () {
  'use strict';

  function addText(parent, className, text) {
    var element = document.createElement('div');
    if (className) element.className = className;
    element.textContent = text;
    parent.appendChild(element);
    return element;
  }

  function createCard(options) {
    var card = document.createElement(options.href ? 'a' : 'div');
    card.className = 'tier-card' + (options.modifier ? ' ' + options.modifier : '');
    card.tabIndex = 0;

    if (options.href) {
      card.href = options.href;
      card.target = '_blank';
      card.rel = 'noopener noreferrer';
    }

    var cover = document.createElement('div');
    cover.className = 'tier-card-cover';

    var image = document.createElement('img');
    image.className = 'tier-card-image';
    image.src = options.image || '/assets/no_image.png';
    image.alt = options.imageAlt || '';
    image.loading = 'lazy';
    image.decoding = 'async';
    image.addEventListener('error', function () {
      if (image.dataset.fallbackApplied) return;
      image.dataset.fallbackApplied = 'true';
      image.src = options.fallbackImage || '/assets/no_image.png';
    });
    cover.appendChild(image);

    if (options.badge != null && options.badge !== '') {
      addText(cover, 'tier-card-badge', String(options.badge));
    }

    if (options.note) {
      addText(cover, 'tier-card-note', options.note);
    }

    card.appendChild(cover);
    addText(card, 'tier-card-title', options.title);

    if (options.ariaLabel) card.setAttribute('aria-label', options.ariaLabel);
    return card;
  }

  function render(options) {
    var root = options.root;
    var tiers = options.tiers || [];
    var items = options.items || [];
    var idPrefix = options.idPrefix || 'tier-list';

    root.replaceChildren();

    tiers.forEach(function (definition) {
      var tierItems = items.filter(function (item) {
        return options.getTier(item) === definition.key;
      });

      var row = document.createElement('section');
      row.className = 'tier-board-row';
      row.dataset.tier = definition.key;
      row.setAttribute('aria-labelledby', idPrefix + '-tier-' + definition.key);

      var rail = document.createElement('div');
      rail.className = 'tier-board-rail';
      var heading = addText(rail, 'tier-board-letter', definition.label);
      heading.id = idPrefix + '-tier-' + definition.key;
      if (definition.description) {
        rail.tabIndex = 0;
        rail.dataset.tierDescription = definition.description;
        rail.setAttribute(
          'aria-label',
          definition.label + ' tier: ' + definition.description
        );
      }
      addText(
        rail,
        'tier-board-count',
        tierItems.length + (tierItems.length === 1 ? ' title' : ' titles')
      );
      row.appendChild(rail);

      var list = document.createElement('div');
      list.className = 'tier-board-items';
      if (!tierItems.length) {
        addText(
          list,
          'tier-board-empty',
          typeof options.emptyMessage === 'function'
            ? options.emptyMessage(definition)
            : options.emptyMessage || 'No titles in this tier.'
        );
      } else {
        tierItems.forEach(function (item, index) {
          var card = options.createCard(item, definition, index);
          if (card) list.appendChild(card);
        });
      }
      row.appendChild(list);
      root.appendChild(row);
    });

    root.setAttribute('aria-busy', 'false');
  }

  function positionTooltip(tooltip, anchor, gap) {
    var anchorRect = anchor.getBoundingClientRect();
    var tooltipRect = tooltip.getBoundingClientRect();
    var spacing = gap == null ? 10 : gap;
    var left = anchorRect.left + anchorRect.width / 2 - tooltipRect.width / 2;
    left = Math.max(12, Math.min(left, window.innerWidth - tooltipRect.width - 12));

    var top = anchorRect.top - tooltipRect.height - spacing;
    if (top < 12) {
      top = Math.min(window.innerHeight - tooltipRect.height - 12, anchorRect.bottom + spacing);
    }

    tooltip.style.left = Math.round(left) + 'px';
    tooltip.style.top = Math.round(top) + 'px';
  }

  window.TierList = Object.freeze({
    addText: addText,
    createCard: createCard,
    positionTooltip: positionTooltip,
    render: render
  });
})();
