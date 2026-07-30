(function () {
  'use strict';

  var PROFILE_ORDER = ['Kan', 'Demi', 'Goku', 'Orhan'];
  var TIER_NAMES = {
    1: 'Masterpiece',
    2: 'Awesome',
    3: 'Suggestable',
    4: 'Watchable',
    5: 'Not worth watching'
  };
  var TIERS = [
    { key: 's', label: 'S' },
    { key: 'a', label: 'A' },
    { key: 'b', label: 'B' },
    { key: 'c', label: 'C' },
    { key: 'd', label: 'D' }
  ];

  var config = window.ANIME_CONFIG;
  var tierList = window.TierList;
  var board = document.getElementById('anime-board');
  var status = document.getElementById('anime-status');
  var search = document.getElementById('anime-search');
  var voterFilter = document.getElementById('anime-voter-filter');
  var voterTrigger = document.getElementById('anime-voter-trigger');
  var voterOptions = document.getElementById('anime-voter-options');
  var voterSummary = document.getElementById('anime-voter-summary');
  var tooltip = document.getElementById('anime-tooltip');
  var activeTooltipCard = null;
  var state = {
    profiles: [],
    animes: [],
    ratings: [],
    tags: [],
    query: '',
    selectedVoterIds: []
  };

  function setStatus(message, kind) {
    status.textContent = message;
    status.hidden = !message;
    if (kind) status.dataset.kind = kind;
    else delete status.dataset.kind;
  }

  function api(path) {
    return fetch(config.supabaseUrl + '/rest/v1/' + path, {
      headers: {
        apikey: config.supabaseAnonKey,
        Authorization: 'Bearer ' + config.supabaseAnonKey
      }
    }).then(function (response) {
      if (!response.ok) {
        throw new Error('Supabase returned ' + response.status + ' for ' + path);
      }
      return response.json();
    });
  }

  function profileFor(userId) {
    return state.profiles.find(function (profile) {
      return profile.id === userId;
    });
  }

  function profileOrder(name) {
    var index = PROFILE_ORDER.indexOf(name);
    return index === -1 ? PROFILE_ORDER.length : index;
  }

  function sortedProfiles() {
    return state.profiles
      .filter(function (profile) {
        return profile.display_name;
      })
      .slice()
      .sort(function (a, b) {
        return profileOrder(a.display_name) - profileOrder(b.display_name) ||
          a.display_name.localeCompare(b.display_name);
      });
  }

  function voterIsSelected(userId) {
    return !state.selectedVoterIds.length || state.selectedVoterIds.includes(userId);
  }

  function ratingsFor(animeId) {
    return state.ratings
      .filter(function (rating) {
        return rating.anime_id === animeId && voterIsSelected(rating.user_id);
      })
      .map(function (rating) {
        var profile = profileFor(rating.user_id);
        return {
          name: profile ? profile.display_name : 'Unknown',
          tier: Number(rating.tier)
        };
      })
      .sort(function (a, b) {
        return profileOrder(a.name) - profileOrder(b.name) || a.name.localeCompare(b.name);
      });
  }

  function tagsFor(animeId) {
    return state.tags
      .filter(function (tag) {
        return tag.anime_id === animeId &&
          voterIsSelected(tag.user_id) &&
          String(tag.tag || '').trim();
      })
      .map(function (tag) {
        var profile = profileFor(tag.user_id);
        return {
          name: profile ? profile.display_name : 'Unknown',
          text: String(tag.tag).trim()
        };
      })
      .sort(function (a, b) {
        return profileOrder(a.name) - profileOrder(b.name) || a.name.localeCompare(b.name);
      });
  }

  function averageFor(animeId) {
    var ratings = ratingsFor(animeId);
    if (!ratings.length) return null;
    return ratings.reduce(function (sum, rating) {
      return sum + rating.tier;
    }, 0) / ratings.length;
  }

  function tierFor(score) {
    if (score == null) return 'unrated';
    var roundedScore = Math.round((score + Number.EPSILON) * 100) / 100;
    if (roundedScore <= 1.5) return 's';
    if (roundedScore <= 2.5) return 'a';
    if (roundedScore <= 3.5) return 'b';
    if (roundedScore <= 4.5) return 'c';
    return 'd';
  }

  function scoreForDisplay(item) {
    if (item.average == null) return '—';
    if (item.ratings.length === 1) return String(item.ratings[0].tier);
    return item.average.toFixed(2);
  }

  function preparedAnimes() {
    return state.animes
      .map(function (anime) {
        var ratings = ratingsFor(anime.id);
        var average = averageFor(anime.id);
        return {
          anime: anime,
          ratings: ratings,
          tags: tagsFor(anime.id),
          average: average,
          tier: tierFor(average)
        };
      })
      .filter(function (item) {
        return !state.query || item.anime.title.toLocaleLowerCase().includes(state.query);
      })
      .sort(function (a, b) {
        if (a.average == null && b.average != null) return 1;
        if (a.average != null && b.average == null) return -1;
        if (a.average !== b.average) return a.average - b.average;
        if (a.ratings.length !== b.ratings.length) return b.ratings.length - a.ratings.length;
        return a.anime.title.localeCompare(b.anime.title);
      });
  }

  function addText(parent, className, text) {
    var element = document.createElement('div');
    element.className = className;
    element.textContent = text;
    parent.appendChild(element);
    return element;
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

  function tooltipRow(parent, label, value) {
    var row = document.createElement('div');
    row.className = 'tier-tooltip-row';
    addText(row, '', label);
    addText(row, '', value);
    parent.appendChild(row);
  }

  function ratingLabel(tier) {
    var name = TIER_NAMES[tier];
    return name ? 'Tier ' + tier + ' (' + name + ')' : 'Tier ' + tier;
  }

  function buildTooltip(item) {
    tooltip.replaceChildren();
    addText(tooltip, 'tier-tooltip-title', item.anime.title);
    if (item.ratings.length === 1) {
      addText(
        tooltip,
        'tier-tooltip-meta',
        item.ratings[0].name + ' scored this ' + item.ratings[0].tier
      );
    } else {
      addText(
        tooltip,
        'tier-tooltip-meta',
        item.average == null
          ? 'No votes yet'
          : 'Average ' + item.average.toFixed(2) + ' from ' + item.ratings.length + ' votes'
      );
    }

    if (item.ratings.length) {
      addText(tooltip, 'tier-tooltip-section', 'Votes');
      item.ratings.forEach(function (rating) {
        tooltipRow(tooltip, rating.name, ratingLabel(rating.tier));
      });
    }

    if (item.tags.length) {
      addText(tooltip, 'tier-tooltip-section', 'Comments');
      item.tags.forEach(function (tag) {
        tooltipRow(tooltip, tag.name, tag.text);
      });
    }
  }

  function showTooltip(card, item) {
    activeTooltipCard = card;
    buildTooltip(item);
    tooltip.hidden = false;
    tierList.positionTooltip(tooltip, card);
    card.setAttribute('aria-describedby', 'anime-tooltip');
  }

  function hideTooltip(card) {
    tooltip.hidden = true;
    card.removeAttribute('aria-describedby');
    if (activeTooltipCard === card) activeTooltipCard = null;
  }

  function handleViewportChange() {
    if (!tooltip.hidden && activeTooltipCard === document.activeElement) {
      tierList.positionTooltip(tooltip, activeTooltipCard);
      return;
    }
    if (activeTooltipCard) hideTooltip(activeTooltipCard);
    else tooltip.hidden = true;
  }

  function createCard(item) {
    var externalUrl = safeExternalUrl(item.anime.url);
    var tagText = '';
    if (item.tags.length) {
      tagText = item.tags[0].text;
      if (item.tags.length > 1) tagText += ' +' + (item.tags.length - 1);
    }

    var aria = item.anime.title + '. ';
    aria += item.ratings.length === 1
      ? item.ratings[0].name + ' score ' + item.ratings[0].tier + '.'
      : 'Average ' + item.average.toFixed(2) + '.';
    if (item.ratings.length) {
      aria += ' Votes: ' + item.ratings.map(function (rating) {
        return rating.name + ' ' + ratingLabel(rating.tier);
      }).join(', ') + '.';
    }
    if (item.tags.length) {
      aria += ' Comments: ' + item.tags.map(function (tag) {
        return tag.name + ': ' + tag.text;
      }).join(', ') + '.';
    }

    var card = tierList.createCard({
      title: item.anime.title,
      image: item.anime.poster_url,
      href: externalUrl,
      badge: scoreForDisplay(item),
      note: tagText,
      ariaLabel: aria
    });

    card.addEventListener('mouseenter', function () {
      showTooltip(card, item);
    });
    card.addEventListener('mouseleave', function () {
      hideTooltip(card);
    });
    card.addEventListener('focus', function () {
      showTooltip(card, item);
    });
    card.addEventListener('blur', function () {
      hideTooltip(card);
    });

    return card;
  }

  function render() {
    var items = preparedAnimes().filter(function (item) {
      return item.average != null;
    });
    tierList.render({
      root: board,
      tiers: TIERS,
      items: items,
      idPrefix: 'anime',
      getTier: function (item) {
        return item.tier;
      },
      createCard: createCard,
      emptyMessage: state.query ? 'No matches in this tier.' : 'No titles in this tier yet.'
    });

    if (state.query) {
      setStatus(items.length + (items.length === 1 ? ' matching title' : ' matching titles') + '.');
    } else {
      setStatus('');
    }
  }

  function hideActiveTooltip() {
    if (activeTooltipCard) hideTooltip(activeTooltipCard);
    else tooltip.hidden = true;
  }

  function createVoterOption(value, label, checked) {
    var option = document.createElement('label');
    option.className = 'anime-voter-option';

    var input = document.createElement('input');
    input.type = 'checkbox';
    input.value = value;
    input.checked = checked;
    option.appendChild(input);

    var text = document.createElement('span');
    text.textContent = label;
    option.appendChild(text);

    var check = document.createElement('span');
    check.className = 'anime-voter-check';
    check.setAttribute('aria-hidden', 'true');
    option.appendChild(check);
    voterOptions.appendChild(option);
  }

  function updateVoterSummary() {
    if (!state.selectedVoterIds.length) {
      voterSummary.textContent = 'All';
      return;
    }

    var names = sortedProfiles()
      .filter(function (profile) {
        return state.selectedVoterIds.includes(profile.id);
      })
      .map(function (profile) {
        return profile.display_name;
      });

    if (names.length <= 2) voterSummary.textContent = names.join(' + ');
    else voterSummary.textContent = names.length + ' voters';
  }

  function renderVoterOptions() {
    voterOptions.querySelectorAll('.anime-voter-option').forEach(function (option) {
      option.remove();
    });
    createVoterOption('all', 'All', !state.selectedVoterIds.length);
    sortedProfiles().forEach(function (profile) {
      createVoterOption(
        profile.id,
        profile.display_name,
        state.selectedVoterIds.includes(profile.id)
      );
    });
    updateVoterSummary();
  }

  function syncVoterOptions() {
    voterOptions.querySelectorAll('input[type="checkbox"]').forEach(function (input) {
      input.checked = input.value === 'all'
        ? !state.selectedVoterIds.length
        : state.selectedVoterIds.includes(input.value);
    });
    updateVoterSummary();
  }

  function voterMenuIsOpen() {
    return voterTrigger.getAttribute('aria-expanded') === 'true';
  }

  function setVoterMenuOpen(open, focusPosition) {
    voterTrigger.setAttribute('aria-expanded', String(open));
    voterOptions.hidden = !open;

    if (!open || !focusPosition) return;
    var inputs = voterOptions.querySelectorAll('input[type="checkbox"]');
    if (!inputs.length) return;
    inputs[focusPosition === 'last' ? inputs.length - 1 : 0].focus();
  }

  function moveVoterOptionFocus(event) {
    var inputs = Array.from(voterOptions.querySelectorAll('input[type="checkbox"]'));
    if (!inputs.length) return;

    var currentIndex = inputs.indexOf(document.activeElement);
    var nextIndex;
    if (event.key === 'Home') nextIndex = 0;
    else if (event.key === 'End') nextIndex = inputs.length - 1;
    else if (event.key === 'ArrowDown') nextIndex = (currentIndex + 1) % inputs.length;
    else if (event.key === 'ArrowUp') {
      nextIndex = (currentIndex - 1 + inputs.length) % inputs.length;
    } else {
      return;
    }

    event.preventDefault();
    inputs[nextIndex].focus();
  }

  function handleVoterChange(event) {
    var input = event.target;
    if (!(input instanceof HTMLInputElement) || input.type !== 'checkbox') return;

    if (input.value === 'all') {
      state.selectedVoterIds = [];
    } else if (input.checked) {
      state.selectedVoterIds = state.selectedVoterIds.concat(input.value);
    } else {
      state.selectedVoterIds = state.selectedVoterIds.filter(function (userId) {
        return userId !== input.value;
      });
    }

    syncVoterOptions();
    hideActiveTooltip();
    render();
  }

  function init() {
    if (!tierList) {
      setStatus('The shared tier-list component could not be loaded.', 'error');
      board.setAttribute('aria-busy', 'false');
      return;
    }

    if (!config || !config.supabaseUrl || !config.supabaseAnonKey) {
      setStatus('The public Supabase configuration is missing.', 'error');
      board.setAttribute('aria-busy', 'false');
      return;
    }

    Promise.all([
      api('profiles?select=id,display_name'),
      api('animes?select=id,title,url,poster_url'),
      api('ratings?select=anime_id,user_id,tier'),
      api('anime_tags?select=anime_id,user_id,tag')
    ])
      .then(function (results) {
        state.profiles = results[0];
        state.animes = results[1];
        state.ratings = results[2];
        state.tags = results[3];
        renderVoterOptions();
        render();
      })
      .catch(function (error) {
        console.error(error);
        setStatus('The anime list could not be loaded. Try refreshing the page.', 'error');
        board.setAttribute('aria-busy', 'false');
      });

    search.addEventListener('input', function () {
      state.query = search.value.trim().toLocaleLowerCase();
      hideActiveTooltip();
      render();
    });

    voterOptions.addEventListener('change', handleVoterChange);
    voterTrigger.addEventListener('click', function () {
      setVoterMenuOpen(!voterMenuIsOpen());
    });
    voterTrigger.addEventListener('keydown', function (event) {
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        setVoterMenuOpen(true, event.key === 'ArrowUp' ? 'last' : 'first');
      } else if (event.key === 'Escape' && voterMenuIsOpen()) {
        event.preventDefault();
        setVoterMenuOpen(false);
      }
    });
    voterOptions.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        event.preventDefault();
        setVoterMenuOpen(false);
        voterTrigger.focus();
        return;
      }
      moveVoterOptionFocus(event);
    });
    document.addEventListener('click', function (event) {
      if (voterMenuIsOpen() && !voterFilter.contains(event.target)) {
        setVoterMenuOpen(false);
      }
    });

    window.addEventListener('scroll', handleViewportChange, true);
    window.addEventListener('resize', handleViewportChange);
  }

  init();
})();
