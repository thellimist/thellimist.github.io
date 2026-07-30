(function () {
  'use strict';

  var TIERS = [
    { key: 's', label: 'S' },
    { key: 'a', label: 'A' },
    { key: 'b', label: 'B' },
    { key: 'c', label: 'C' },
    { key: 'd', label: 'D' }
  ];

  var tierList = window.TierList;
  var board = document.getElementById('chocolate-board');
  var status = document.getElementById('chocolate-status');
  var countryFilter = document.getElementById('country-filter');
  var brandFilter = document.getElementById('brand-filter');
  var tooltip = document.getElementById('chocolate-tooltip');
  var allChocolates = [];
  var activeCard = null;
  var hideTimer = null;

  function setStatus(message, kind) {
    status.textContent = message;
    status.hidden = !message;
    if (kind) status.dataset.kind = kind;
    else delete status.dataset.kind;
  }

  function safeExternalUrl(value) {
    if (!value) return null;
    try {
      var parsed = new URL(value, window.location.origin);
      return parsed.protocol === 'http:' || parsed.protocol === 'https:' ? parsed.href : null;
    } catch (error) {
      return null;
    }
  }

  function countriesFor(chocolate) {
    if (!chocolate.country) return [];
    return Array.isArray(chocolate.country) ? chocolate.country : [chocolate.country];
  }

  function addTooltipRow(label, value) {
    var row = document.createElement('div');
    row.className = 'tier-tooltip-row';
    tierList.addText(row, '', label);
    if (value instanceof Node) {
      row.appendChild(value);
    } else {
      tierList.addText(row, '', value);
    }
    tooltip.appendChild(row);
  }

  function buildTooltip(chocolate) {
    tooltip.replaceChildren();
    tierList.addText(tooltip, 'tier-tooltip-title', chocolate.name);

    if (chocolate.brand) addTooltipRow('Brand', chocolate.brand);
    if (countriesFor(chocolate).length) {
      addTooltipRow('Country', countriesFor(chocolate).join(', '));
    }

    var location = safeExternalUrl(chocolate.location);
    if (location) {
      addTooltipRow('Location', 'Open card for Maps');
    }

    if (chocolate.comments) {
      tierList.addText(tooltip, 'tier-tooltip-section', 'Comments');
      tierList.addText(tooltip, 'tier-tooltip-meta', chocolate.comments);
    }
  }

  function cancelHide() {
    if (!hideTimer) return;
    window.clearTimeout(hideTimer);
    hideTimer = null;
  }

  function hideTooltip() {
    cancelHide();
    tooltip.hidden = true;
    if (activeCard) activeCard.removeAttribute('aria-describedby');
    activeCard = null;
  }

  function hideTooltipSoon() {
    cancelHide();
    hideTimer = window.setTimeout(hideTooltip, 120);
  }

  function showTooltip(card, chocolate) {
    cancelHide();
    if (activeCard && activeCard !== card) {
      activeCard.removeAttribute('aria-describedby');
    }
    activeCard = card;
    buildTooltip(chocolate);
    tooltip.hidden = false;
    tierList.positionTooltip(tooltip, card);
    card.setAttribute('aria-describedby', 'chocolate-tooltip');
  }

  function handleViewportChange() {
    if (!tooltip.hidden && activeCard === document.activeElement) {
      tierList.positionTooltip(tooltip, activeCard);
      return;
    }
    hideTooltip();
  }

  function createChocolateCard(chocolate) {
    var location = safeExternalUrl(chocolate.location);
    var details = [chocolate.name];
    if (chocolate.brand) details.push('Brand: ' + chocolate.brand);
    if (countriesFor(chocolate).length) {
      details.push('Country: ' + countriesFor(chocolate).join(', '));
    }
    if (chocolate.comments) details.push('Comments: ' + chocolate.comments);
    if (location) details.push('Opens location in Maps');

    var card = tierList.createCard({
      title: chocolate.name,
      image: chocolate.picture,
      href: location,
      imageAlt: chocolate.name + ' package',
      note: chocolate.comments || '',
      modifier: 'tier-card--product',
      ariaLabel: details.join('. ') + '.'
    });

    card.addEventListener('mouseenter', function () {
      showTooltip(card, chocolate);
    });
    card.addEventListener('mouseleave', hideTooltipSoon);
    card.addEventListener('focus', function () {
      showTooltip(card, chocolate);
    });
    card.addEventListener('blur', function (event) {
      if (!tooltip.contains(event.relatedTarget)) hideTooltipSoon();
    });

    return card;
  }

  function renderChocolates(chocolates) {
    hideTooltip();
    tierList.render({
      root: board,
      tiers: TIERS,
      items: chocolates,
      idPrefix: 'chocolate',
      getTier: function (chocolate) {
        return String(chocolate.tier || '').toLocaleLowerCase();
      },
      createCard: createChocolateCard,
      emptyMessage: 'No matches in this tier.'
    });
  }

  function applyFilters() {
    var selectedCountry = countryFilter.value;
    var selectedBrand = brandFilter.value;
    var filtered = allChocolates.filter(function (chocolate) {
      var matchesCountry = !selectedCountry || countriesFor(chocolate).includes(selectedCountry);
      var matchesBrand = !selectedBrand || chocolate.brand === selectedBrand;
      return matchesCountry && matchesBrand;
    });
    renderChocolates(filtered);
  }

  function populateFilters(chocolates) {
    var countries = new Set();
    var brands = new Set();

    chocolates.forEach(function (chocolate) {
      countriesFor(chocolate).filter(Boolean).forEach(function (country) {
        countries.add(country);
      });
      if (chocolate.brand) brands.add(chocolate.brand);
    });

    Array.from(countries).sort().forEach(function (country) {
      var option = document.createElement('option');
      option.value = country;
      option.textContent = country;
      countryFilter.appendChild(option);
    });

    Array.from(brands).sort().forEach(function (brand) {
      var option = document.createElement('option');
      option.value = brand;
      option.textContent = brand;
      brandFilter.appendChild(option);
    });
  }

  function init() {
    if (!tierList) {
      setStatus('The shared tier-list component could not be loaded.', 'error');
      board.setAttribute('aria-busy', 'false');
      return;
    }

    fetch('/chocolate/chocolates.json')
      .then(function (response) {
        if (!response.ok) throw new Error('Chocolate data returned ' + response.status);
        return response.json();
      })
      .then(function (chocolates) {
        allChocolates = chocolates;
        populateFilters(chocolates);
        renderChocolates(chocolates);
        setStatus('');
      })
      .catch(function (error) {
        console.error(error);
        renderChocolates([]);
        setStatus('The chocolate list could not be loaded. Try refreshing the page.', 'error');
      });

    countryFilter.addEventListener('change', applyFilters);
    brandFilter.addEventListener('change', applyFilters);
    tooltip.addEventListener('mouseenter', cancelHide);
    tooltip.addEventListener('mouseleave', hideTooltipSoon);
    window.addEventListener('scroll', handleViewportChange, true);
    window.addEventListener('resize', handleViewportChange);
  }

  init();
})();
