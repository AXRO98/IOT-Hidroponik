/**
 * AdminLTE Demo Menu with localStorage Persistence
 * =================================================
 * File: demo.js
 * 
 * DESKRIPSI:
 *   File ini adalah modifikasi dari demo.js bawaan AdminLTE yang
 *   ditambahkan fitur penyimpanan otomatis ke localStorage. Setiap
 *   perubahan pada kontrol (checkbox/select) akan langsung disimpan,
 *   dan saat halaman dimuat ulang, semua pengaturan akan dikembalikan
 *   sesuai nilai yang tersimpan.
 * 
 * FITUR:
 *   - Dark Mode
 *   - Header Options (Fixed, Dropdown Legacy, No Border)
 *   - Sidebar Options (Collapsed, Fixed, Mini, Nav Style, dll.)
 *   - Footer Fixed
 *   - Small Text Options (Body, Navbar, Brand, Sidebar, Footer)
 *   - Navbar Variants (warna navbar)
 *   - Accent Color Variants
 *   - Dark/Light Sidebar Variants
 *   - Brand Logo Variants
 *   - Tombol Reset (menghapus semua localStorage dan reload)
 * 
 * CARA KERJA:
 *   - Setiap elemen kontrol diberi atribut `data-storage-key` yang
 *     berisi kunci unik untuk localStorage.
 *   - Fungsi `applyLocalStorageToUI()` membaca localStorage dan
 *     menerapkan nilai ke elemen (checked/selected) serta memicu
 *     event `change` agar class pada body berubah.
 *   - Fungsi `setupSaveListeners()` menyimpan perubahan ke localStorage
 *     setiap kali ada event change pada kontrol.
 *   - Fungsi `loadSettings()` (dipertahankan dari versi sebelumnya)
 *     langsung mengaplikasikan class berdasarkan localStorage tanpa
 *     melalui event. Keduanya dipanggil agar kompatibel.
 *   - Fungsi `addResetButton()` menambahkan tombol reset di bagian
 *     bawah panel.
 * 
 * DEPENDENSI:
 *   - jQuery (digunakan oleh AdminLTE)
 * 
 * PENGGUNAAN:
 *   1. Pastikan file ini dipanggil setelah jQuery dan AdminLTE.
 *   2. Control sidebar harus memiliki class `control-sidebar`.
 *   3. Semua elemen akan dibuat otomatis oleh script ini.
 * 
 * --------------------------------------------------------------------
 */

(function ($) {
  'use strict'

  // ==================================================================
  //  LOAD SETTINGS (langsung menerapkan class dari localStorage)
  // ==================================================================
  function loadSettings() {
    // Dark Mode
    if (localStorage.getItem('darkMode') === 'true') {
      $('body').addClass('dark-mode')
    } else if (localStorage.getItem('darkMode') === 'false') {
      $('body').removeClass('dark-mode')
    }

    // Header fixed
    if (localStorage.getItem('headerFixed') === 'true') {
      $('body').addClass('layout-navbar-fixed')
    } else if (localStorage.getItem('headerFixed') === 'false') {
      $('body').removeClass('layout-navbar-fixed')
    }

    // Dropdown legacy offset
    if (localStorage.getItem('dropdownLegacy') === 'true') {
      $('.main-header').addClass('dropdown-legacy')
    } else if (localStorage.getItem('dropdownLegacy') === 'false') {
      $('.main-header').removeClass('dropdown-legacy')
    }

    // No border
    if (localStorage.getItem('noBorder') === 'true') {
      $('.main-header').addClass('border-bottom-0')
    } else if (localStorage.getItem('noBorder') === 'false') {
      $('.main-header').removeClass('border-bottom-0')
    }

    // Sidebar collapsed
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
      $('body').addClass('sidebar-collapse')
    } else if (localStorage.getItem('sidebarCollapsed') === 'false') {
      $('body').removeClass('sidebar-collapse')
    }

    // Sidebar fixed
    if (localStorage.getItem('sidebarFixed') === 'true') {
      $('body').addClass('layout-fixed')
    } else if (localStorage.getItem('sidebarFixed') === 'false') {
      $('body').removeClass('layout-fixed')
    }

    // Sidebar mini
    if (localStorage.getItem('sidebarMini') === 'true') {
      $('body').addClass('sidebar-mini')
    } else if (localStorage.getItem('sidebarMini') === 'false') {
      $('body').removeClass('sidebar-mini')
    }

    // Sidebar mini MD
    if (localStorage.getItem('sidebarMiniMD') === 'true') {
      $('body').addClass('sidebar-mini-md')
    } else if (localStorage.getItem('sidebarMiniMD') === 'false') {
      $('body').removeClass('sidebar-mini-md')
    }

    // Sidebar mini XS
    if (localStorage.getItem('sidebarMiniXS') === 'true') {
      $('body').addClass('sidebar-mini-xs')
    } else if (localStorage.getItem('sidebarMiniXS') === 'false') {
      $('body').removeClass('sidebar-mini-xs')
    }

    // Nav flat style
    if (localStorage.getItem('navFlat') === 'true') {
      $('.nav-sidebar').addClass('nav-flat')
    } else if (localStorage.getItem('navFlat') === 'false') {
      $('.nav-sidebar').removeClass('nav-flat')
    }

    // Nav legacy style
    if (localStorage.getItem('navLegacy') === 'true') {
      $('.nav-sidebar').addClass('nav-legacy')
    } else if (localStorage.getItem('navLegacy') === 'false') {
      $('.nav-sidebar').removeClass('nav-legacy')
    }

    // Nav compact
    if (localStorage.getItem('navCompact') === 'true') {
      $('.nav-sidebar').addClass('nav-compact')
    } else if (localStorage.getItem('navCompact') === 'false') {
      $('.nav-sidebar').removeClass('nav-compact')
    }

    // Nav child indent
    if (localStorage.getItem('navChildIndent') === 'true') {
      $('.nav-sidebar').addClass('nav-child-indent')
    } else if (localStorage.getItem('navChildIndent') === 'false') {
      $('.nav-sidebar').removeClass('nav-child-indent')
    }

    // Nav child hide on collapse
    if (localStorage.getItem('navChildHide') === 'true') {
      $('.nav-sidebar').addClass('nav-collapse-hide-child')
    } else if (localStorage.getItem('navChildHide') === 'false') {
      $('.nav-sidebar').removeClass('nav-collapse-hide-child')
    }

    // Disable hover auto-expand
    if (localStorage.getItem('disableHover') === 'true') {
      $('.main-sidebar').addClass('sidebar-no-expand')
    } else if (localStorage.getItem('disableHover') === 'false') {
      $('.main-sidebar').removeClass('sidebar-no-expand')
    }

    // Footer fixed
    if (localStorage.getItem('footerFixed') === 'true') {
      $('body').addClass('layout-footer-fixed')
    } else if (localStorage.getItem('footerFixed') === 'false') {
      $('body').removeClass('layout-footer-fixed')
    }

    // Small text body
    if (localStorage.getItem('textBody') === 'true') {
      $('body').addClass('text-sm')
    } else if (localStorage.getItem('textBody') === 'false') {
      $('body').removeClass('text-sm')
    }

    // Small text navbar
    if (localStorage.getItem('textNavbar') === 'true') {
      $('.main-header').addClass('text-sm')
    } else if (localStorage.getItem('textNavbar') === 'false') {
      $('.main-header').removeClass('text-sm')
    }

    // Small text brand
    if (localStorage.getItem('textBrand') === 'true') {
      $('.brand-link').addClass('text-sm')
    } else if (localStorage.getItem('textBrand') === 'false') {
      $('.brand-link').removeClass('text-sm')
    }

    // Small text sidebar
    if (localStorage.getItem('textSidebar') === 'true') {
      $('.nav-sidebar').addClass('text-sm')
    } else if (localStorage.getItem('textSidebar') === 'false') {
      $('.nav-sidebar').removeClass('text-sm')
    }

    // Small text footer
    if (localStorage.getItem('textFooter') === 'true') {
      $('.main-footer').addClass('text-sm')
    } else if (localStorage.getItem('textFooter') === 'false') {
      $('.main-footer').removeClass('text-sm')
    }

    // Navbar variant
    var navbarVariant = localStorage.getItem('navbarVariant')
    if (navbarVariant) {
      var $mainHeader = $('.main-header')
      // Hapus semua class navbar
      $mainHeader.removeClass('navbar-dark navbar-light')
      navbar_dark_skins.concat(navbar_light_skins).forEach(function (cls) {
        $mainHeader.removeClass(cls)
      })
      $mainHeader.addClass(navbarVariant)
      if (navbar_dark_skins.indexOf(navbarVariant) > -1) {
        $mainHeader.addClass('navbar-dark')
      } else {
        $mainHeader.addClass('navbar-light')
      }
    }

    // Accent color
    var accentVariant = localStorage.getItem('accentVariant')
    if (accentVariant) {
      var $body = $('body')
      accent_colors.forEach(function (cls) {
        $body.removeClass(cls)
      })
      $body.addClass(accentVariant)
    }

    // Dark sidebar variant
    var darkSidebarVariant = localStorage.getItem('darkSidebarVariant')
    if (darkSidebarVariant) {
      var $sidebar = $('.main-sidebar')
      sidebar_skins.forEach(function (cls) {
        $sidebar.removeClass(cls)
      })
      $sidebar.addClass('sidebar-dark-' + darkSidebarVariant.replace('bg-', ''))
      $('.sidebar').removeClass('os-theme-dark').addClass('os-theme-light')
    }

    // Light sidebar variant
    var lightSidebarVariant = localStorage.getItem('lightSidebarVariant')
    if (lightSidebarVariant) {
      var $sidebar = $('.main-sidebar')
      sidebar_skins.forEach(function (cls) {
        $sidebar.removeClass(cls)
      })
      $sidebar.addClass('sidebar-light-' + lightSidebarVariant.replace('bg-', ''))
      $('.sidebar').removeClass('os-theme-light').addClass('os-theme-dark')
    }

    // Brand variant
    var brandVariant = localStorage.getItem('brandVariant')
    if (brandVariant) {
      var $logo = $('.brand-link')
      logo_skins.forEach(function (cls) {
        $logo.removeClass(cls)
      })
      $logo.addClass(brandVariant)
      if (brandVariant === 'navbar-light' || brandVariant === 'navbar-white') {
        $logo.addClass('text-black')
      } else {
        $logo.removeClass('text-black')
      }
    }
  }

  // ==================================================================
  //  HELPER FUNCTIONS (dari demo.js asli)
  // ==================================================================
  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1)
  }

  function createSkinBlock(colors, callback, noneSelected) {
    var $block = $('<select />', {
      class: noneSelected
        ? 'custom-select mb-3 border-0'
        : 'custom-select mb-3 text-light border-0 ' + colors[0].replace(/accent-|navbar-/, 'bg-')
    })

    if (noneSelected) {
      var $default = $('<option />', { text: 'None Selected' })
      if (callback) $default.on('click', callback)
      $block.append($default)
    }

    colors.forEach(function (color) {
      var optionClass = (typeof color === 'object' ? color.join(' ') : color)
        .replace('navbar-', 'bg-')
        .replace('accent-', 'bg-')
      var optionText = capitalizeFirstLetter(
        (typeof color === 'object' ? color.join(' ') : color)
          .replace(/navbar-|accent-|bg-/, '')
          .replace('-', ' ')
      )
      var $color = $('<option />', {
        class: optionClass,
        text: optionText
      })
      $block.append($color)
      $color.data('color', color)
      if (callback) $color.on('click', callback)
    })

    return $block
  }

  // ==================================================================
  //  KONSTANTA WARNA (dari demo.js asli)
  // ==================================================================
  var navbar_dark_skins = [
    'navbar-primary', 'navbar-secondary', 'navbar-info', 'navbar-success',
    'navbar-danger', 'navbar-indigo', 'navbar-purple', 'navbar-pink',
    'navbar-navy', 'navbar-lightblue', 'navbar-teal', 'navbar-cyan',
    'navbar-dark', 'navbar-gray-dark', 'navbar-gray'
  ]

  var navbar_light_skins = [
    'navbar-light', 'navbar-warning', 'navbar-white', 'navbar-orange'
  ]

  var sidebar_colors = [
    'bg-primary', 'bg-warning', 'bg-info', 'bg-danger', 'bg-success',
    'bg-indigo', 'bg-lightblue', 'bg-navy', 'bg-purple', 'bg-fuchsia',
    'bg-pink', 'bg-maroon', 'bg-orange', 'bg-lime', 'bg-teal', 'bg-olive'
  ]

  var accent_colors = [
    'accent-primary', 'accent-warning', 'accent-info', 'accent-danger',
    'accent-success', 'accent-indigo', 'accent-lightblue', 'accent-navy',
    'accent-purple', 'accent-fuchsia', 'accent-pink', 'accent-maroon',
    'accent-orange', 'accent-lime', 'accent-teal', 'accent-olive'
  ]

  var sidebar_skins = [
    'sidebar-dark-primary', 'sidebar-dark-warning', 'sidebar-dark-info',
    'sidebar-dark-danger', 'sidebar-dark-success', 'sidebar-dark-indigo',
    'sidebar-dark-lightblue', 'sidebar-dark-navy', 'sidebar-dark-purple',
    'sidebar-dark-fuchsia', 'sidebar-dark-pink', 'sidebar-dark-maroon',
    'sidebar-dark-orange', 'sidebar-dark-lime', 'sidebar-dark-teal',
    'sidebar-dark-olive', 'sidebar-light-primary', 'sidebar-light-warning',
    'sidebar-light-info', 'sidebar-light-danger', 'sidebar-light-success',
    'sidebar-light-indigo', 'sidebar-light-lightblue', 'sidebar-light-navy',
    'sidebar-light-purple', 'sidebar-light-fuchsia', 'sidebar-light-pink',
    'sidebar-light-maroon', 'sidebar-light-orange', 'sidebar-light-lime',
    'sidebar-light-teal', 'sidebar-light-olive'
  ]

  var navbar_all_colors = navbar_dark_skins.concat(navbar_light_skins)
  var logo_skins = navbar_all_colors

  // ==================================================================
  //  MEMBANGUN CONTROL SIDEBAR (semua elemen)
  // ==================================================================
  var $sidebar = $('.control-sidebar')
  var $container = $('<div />', { class: 'p-3 control-sidebar-content' })
  $sidebar.append($container)

  $container.append('<h5>Customize AdminLTE</h5><hr class="mb-2"/>')

  // ------------------------------------------------------------------
  // Dark Mode
  // ------------------------------------------------------------------
  var $darkModeCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('body').hasClass('dark-mode'),
    class: 'mr-1'
  }).attr('data-storage-key', 'darkMode')
    .on('click', function () {
      $(this).is(':checked')
        ? $('body').addClass('dark-mode')
        : $('body').removeClass('dark-mode')
    })
  $container.append($('<div />', { class: 'mb-4' })
    .append($darkModeCheckbox)
    .append('<span>Dark Mode</span>'))

  // ------------------------------------------------------------------
  // Header Options
  // ------------------------------------------------------------------
  $container.append('<h6>Header Options</h6>')

  // Fixed
  var $headerFixedCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('body').hasClass('layout-navbar-fixed'),
    class: 'mr-1'
  }).attr('data-storage-key', 'headerFixed')
    .on('click', function () {
      $(this).is(':checked')
        ? $('body').addClass('layout-navbar-fixed')
        : $('body').removeClass('layout-navbar-fixed')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($headerFixedCheckbox)
    .append('<span>Fixed</span>'))

  // Dropdown Legacy Offset
  var $dropdownLegacyCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.main-header').hasClass('dropdown-legacy'),
    class: 'mr-1'
  }).attr('data-storage-key', 'dropdownLegacy')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.main-header').addClass('dropdown-legacy')
        : $('.main-header').removeClass('dropdown-legacy')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($dropdownLegacyCheckbox)
    .append('<span>Dropdown Legacy Offset</span>'))

  // No Border
  var $noBorderCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.main-header').hasClass('border-bottom-0'),
    class: 'mr-1'
  }).attr('data-storage-key', 'noBorder')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.main-header').addClass('border-bottom-0')
        : $('.main-header').removeClass('border-bottom-0')
    })
  $container.append($('<div />', { class: 'mb-4' })
    .append($noBorderCheckbox)
    .append('<span>No border</span>'))

  // ------------------------------------------------------------------
  // Sidebar Options
  // ------------------------------------------------------------------
  $container.append('<h6>Sidebar Options</h6>')

  // Collapsed
  var $sidebarCollapsedCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('body').hasClass('sidebar-collapse'),
    class: 'mr-1'
  }).attr('data-storage-key', 'sidebarCollapsed')
    .on('click', function () {
      if ($(this).is(':checked')) {
        $('body').addClass('sidebar-collapse')
        $(window).trigger('resize')
      } else {
        $('body').removeClass('sidebar-collapse')
        $(window).trigger('resize')
      }
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($sidebarCollapsedCheckbox)
    .append('<span>Collapsed</span>'))

  // Sync dengan pushmenu event
  $(document).on('collapsed.lte.pushmenu', '[data-widget="pushmenu"]', function () {
    $sidebarCollapsedCheckbox.prop('checked', true)
  })
  $(document).on('shown.lte.pushmenu', '[data-widget="pushmenu"]', function () {
    $sidebarCollapsedCheckbox.prop('checked', false)
  })

  // Fixed
  var $sidebarFixedCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('body').hasClass('layout-fixed'),
    class: 'mr-1'
  }).attr('data-storage-key', 'sidebarFixed')
    .on('click', function () {
      if ($(this).is(':checked')) {
        $('body').addClass('layout-fixed')
        $(window).trigger('resize')
      } else {
        $('body').removeClass('layout-fixed')
        $(window).trigger('resize')
      }
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($sidebarFixedCheckbox)
    .append('<span>Fixed</span>'))

  // Sidebar Mini
  var $sidebarMiniCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('body').hasClass('sidebar-mini'),
    class: 'mr-1'
  }).attr('data-storage-key', 'sidebarMini')
    .on('click', function () {
      $(this).is(':checked')
        ? $('body').addClass('sidebar-mini')
        : $('body').removeClass('sidebar-mini')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($sidebarMiniCheckbox)
    .append('<span>Sidebar Mini</span>'))

  // Sidebar Mini MD
  var $sidebarMiniMdCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('body').hasClass('sidebar-mini-md'),
    class: 'mr-1'
  }).attr('data-storage-key', 'sidebarMiniMD')
    .on('click', function () {
      $(this).is(':checked')
        ? $('body').addClass('sidebar-mini-md')
        : $('body').removeClass('sidebar-mini-md')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($sidebarMiniMdCheckbox)
    .append('<span>Sidebar Mini MD</span>'))

  // Sidebar Mini XS
  var $sidebarMiniXsCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('body').hasClass('sidebar-mini-xs'),
    class: 'mr-1'
  }).attr('data-storage-key', 'sidebarMiniXS')
    .on('click', function () {
      $(this).is(':checked')
        ? $('body').addClass('sidebar-mini-xs')
        : $('body').removeClass('sidebar-mini-xs')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($sidebarMiniXsCheckbox)
    .append('<span>Sidebar Mini XS</span>'))

  // Nav Flat Style
  var $navFlatCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.nav-sidebar').hasClass('nav-flat'),
    class: 'mr-1'
  }).attr('data-storage-key', 'navFlat')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.nav-sidebar').addClass('nav-flat')
        : $('.nav-sidebar').removeClass('nav-flat')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($navFlatCheckbox)
    .append('<span>Nav Flat Style</span>'))

  // Nav Legacy Style
  var $navLegacyCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.nav-sidebar').hasClass('nav-legacy'),
    class: 'mr-1'
  }).attr('data-storage-key', 'navLegacy')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.nav-sidebar').addClass('nav-legacy')
        : $('.nav-sidebar').removeClass('nav-legacy')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($navLegacyCheckbox)
    .append('<span>Nav Legacy Style</span>'))

  // Nav Compact
  var $navCompactCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.nav-sidebar').hasClass('nav-compact'),
    class: 'mr-1'
  }).attr('data-storage-key', 'navCompact')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.nav-sidebar').addClass('nav-compact')
        : $('.nav-sidebar').removeClass('nav-compact')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($navCompactCheckbox)
    .append('<span>Nav Compact</span>'))

  // Nav Child Indent
  var $navChildIndentCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.nav-sidebar').hasClass('nav-child-indent'),
    class: 'mr-1'
  }).attr('data-storage-key', 'navChildIndent')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.nav-sidebar').addClass('nav-child-indent')
        : $('.nav-sidebar').removeClass('nav-child-indent')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($navChildIndentCheckbox)
    .append('<span>Nav Child Indent</span>'))

  // Nav Child Hide on Collapse
  var $navChildHideCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.nav-sidebar').hasClass('nav-collapse-hide-child'),
    class: 'mr-1'
  }).attr('data-storage-key', 'navChildHide')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.nav-sidebar').addClass('nav-collapse-hide-child')
        : $('.nav-sidebar').removeClass('nav-collapse-hide-child')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($navChildHideCheckbox)
    .append('<span>Nav Child Hide on Collapse</span>'))

  // Disable Hover/Focus Auto-Expand
  var $disableHoverCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.main-sidebar').hasClass('sidebar-no-expand'),
    class: 'mr-1'
  }).attr('data-storage-key', 'disableHover')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.main-sidebar').addClass('sidebar-no-expand')
        : $('.main-sidebar').removeClass('sidebar-no-expand')
    })
  $container.append($('<div />', { class: 'mb-4' })
    .append($disableHoverCheckbox)
    .append('<span>Disable Hover/Focus Auto-Expand</span>'))

  // ------------------------------------------------------------------
  // Footer Options
  // ------------------------------------------------------------------
  $container.append('<h6>Footer Options</h6>')
  var $footerFixedCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('body').hasClass('layout-footer-fixed'),
    class: 'mr-1'
  }).attr('data-storage-key', 'footerFixed')
    .on('click', function () {
      $(this).is(':checked')
        ? $('body').addClass('layout-footer-fixed')
        : $('body').removeClass('layout-footer-fixed')
    })
  $container.append($('<div />', { class: 'mb-4' })
    .append($footerFixedCheckbox)
    .append('<span>Fixed</span>'))

  // ------------------------------------------------------------------
  // Small Text Options
  // ------------------------------------------------------------------
  $container.append('<h6>Small Text Options</h6>')

  // Body
  var $textBodyCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('body').hasClass('text-sm'),
    class: 'mr-1'
  }).attr('data-storage-key', 'textBody')
    .on('click', function () {
      $(this).is(':checked')
        ? $('body').addClass('text-sm')
        : $('body').removeClass('text-sm')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($textBodyCheckbox)
    .append('<span>Body</span>'))

  // Navbar
  var $textNavbarCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.main-header').hasClass('text-sm'),
    class: 'mr-1'
  }).attr('data-storage-key', 'textNavbar')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.main-header').addClass('text-sm')
        : $('.main-header').removeClass('text-sm')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($textNavbarCheckbox)
    .append('<span>Navbar</span>'))

  // Brand
  var $textBrandCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.brand-link').hasClass('text-sm'),
    class: 'mr-1'
  }).attr('data-storage-key', 'textBrand')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.brand-link').addClass('text-sm')
        : $('.brand-link').removeClass('text-sm')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($textBrandCheckbox)
    .append('<span>Brand</span>'))

  // Sidebar Nav
  var $textSidebarCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.nav-sidebar').hasClass('text-sm'),
    class: 'mr-1'
  }).attr('data-storage-key', 'textSidebar')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.nav-sidebar').addClass('text-sm')
        : $('.nav-sidebar').removeClass('text-sm')
    })
  $container.append($('<div />', { class: 'mb-1' })
    .append($textSidebarCheckbox)
    .append('<span>Sidebar Nav</span>'))

  // Footer
  var $textFooterCheckbox = $('<input />', {
    type: 'checkbox',
    value: 1,
    checked: $('.main-footer').hasClass('text-sm'),
    class: 'mr-1'
  }).attr('data-storage-key', 'textFooter')
    .on('click', function () {
      $(this).is(':checked')
        ? $('.main-footer').addClass('text-sm')
        : $('.main-footer').removeClass('text-sm')
    })
  $container.append($('<div />', { class: 'mb-4' })
    .append($textFooterCheckbox)
    .append('<span>Footer</span>'))

  // ------------------------------------------------------------------
  // Navbar Variants (select)
  // ------------------------------------------------------------------
  $container.append('<h6>Navbar Variants</h6>')
  var $navbarVariants = $('<div />', { class: 'd-flex' })
  var $navbarSelect = createSkinBlock(navbar_all_colors, function () {
    var color = $(this).data('color')
    var $mainHeader = $('.main-header')
    $mainHeader.removeClass('navbar-dark navbar-light')
    navbar_all_colors.forEach(function (cls) { $mainHeader.removeClass(cls) })

    $(this).parent()
      .removeClass()
      .addClass('custom-select mb-3 text-light border-0 ')

    if (navbar_dark_skins.indexOf(color) > -1) {
      $mainHeader.addClass('navbar-dark')
      $(this).parent().addClass(color).addClass('text-light')
    } else {
      $mainHeader.addClass('navbar-light')
      $(this).parent().addClass(color)
    }
    $mainHeader.addClass(color)
  })
  $navbarSelect.attr('data-storage-key', 'navbarVariant')

  // Set active class berdasarkan current state
  var activeNavbarColor = null
  $('.main-header')[0].classList.forEach(function (className) {
    if (navbar_all_colors.indexOf(className) > -1 && activeNavbarColor === null) {
      activeNavbarColor = className.replace('navbar-', 'bg-')
    }
  })
  $navbarSelect.find('option.' + activeNavbarColor).prop('selected', true)
  $navbarSelect
    .removeClass()
    .addClass('custom-select mb-3 text-light border-0 ' + activeNavbarColor)

  $navbarVariants.append($navbarSelect)
  $container.append($navbarVariants)

  // ------------------------------------------------------------------
  // Accent Color Variants (select)
  // ------------------------------------------------------------------
  $container.append('<h6>Accent Color Variants</h6>')
  var $accentVariants = $('<div />', { class: 'd-flex' })
  var $accentSelect = createSkinBlock(accent_colors, function () {
    var color = $(this).data('color')
    var $body = $('body')
    accent_colors.forEach(function (cls) { $body.removeClass(cls) })
    $body.addClass(color)
  }, true)
  $accentSelect.attr('data-storage-key', 'accentVariant')
  $accentVariants.append($accentSelect)
  $container.append($accentVariants)

  // ------------------------------------------------------------------
  // Dark Sidebar Variants (select)
  // ------------------------------------------------------------------
  $container.append('<h6>Dark Sidebar Variants</h6>')
  var $sidebarDarkWrapper = $('<div />', { class: 'd-flex' })
  var $sidebarDarkSelect = createSkinBlock(sidebar_colors, function () {
    var color = $(this).data('color')
    var sidebarClass = 'sidebar-dark-' + color.replace('bg-', '')
    var $sidebar = $('.main-sidebar')
    sidebar_skins.forEach(function (cls) { $sidebar.removeClass(cls) })
    $sidebar_light_variants.find('option').prop('selected', false)
    $sidebar.addClass(sidebarClass)
    $('.sidebar').removeClass('os-theme-dark').addClass('os-theme-light')
    $(this).parent()
      .removeClass()
      .addClass('custom-select mb-3 text-light border-0')
      .addClass(color)
  }, true)
  $sidebarDarkSelect.attr('data-storage-key', 'darkSidebarVariant')
  $sidebarDarkWrapper.append($sidebarDarkSelect)
  $container.append($sidebarDarkWrapper)

  var activeDarkSidebarColor = null
  $('.main-sidebar')[0].classList.forEach(function (className) {
    var color = className.replace('sidebar-dark-', 'bg-')
    if (sidebar_colors.indexOf(color) > -1 && activeDarkSidebarColor === null) {
      activeDarkSidebarColor = color
    }
  })
  $sidebarDarkSelect.find('option.' + activeDarkSidebarColor).prop('selected', true)
  $sidebarDarkSelect
    .removeClass()
    .addClass('custom-select mb-3 text-light border-0 ' + activeDarkSidebarColor)

  // ------------------------------------------------------------------
  // Light Sidebar Variants (select)
  // ------------------------------------------------------------------
  $container.append('<h6>Light Sidebar Variants</h6>')
  var $sidebarLightWrapper = $('<div />', { class: 'd-flex' })
  var $sidebarLightSelect = createSkinBlock(sidebar_colors, function () {
    var color = $(this).data('color')
    var sidebarClass = 'sidebar-light-' + color.replace('bg-', '')
    var $sidebar = $('.main-sidebar')
    sidebar_skins.forEach(function (cls) { $sidebar.removeClass(cls) })
    $sidebar_dark_variants.find('option').prop('selected', false)
    $sidebar.addClass(sidebarClass)
    $('.sidebar').removeClass('os-theme-light').addClass('os-theme-dark')
    $(this).parent()
      .removeClass()
      .addClass('custom-select mb-3 text-light border-0')
      .addClass(color)
  }, true)
  $sidebarLightSelect.attr('data-storage-key', 'lightSidebarVariant')
  $sidebarLightWrapper.append($sidebarLightSelect)
  $container.append($sidebarLightWrapper)

  var activeLightSidebarColor = null
  $('.main-sidebar')[0].classList.forEach(function (className) {
    var color = className.replace('sidebar-light-', 'bg-')
    if (sidebar_colors.indexOf(color) > -1 && activeLightSidebarColor === null) {
      activeLightSidebarColor = color
    }
  })
  if (activeLightSidebarColor) {
    $sidebarLightSelect.find('option.' + activeLightSidebarColor).prop('selected', true)
    $sidebarLightSelect
      .removeClass()
      .addClass('custom-select mb-3 text-light border-0 ' + activeLightSidebarColor)
  }

  // ------------------------------------------------------------------
  // Brand Logo Variants (select)
  // ------------------------------------------------------------------
  $container.append('<h6>Brand Logo Variants</h6>')
  var $logoWrapper = $('<div />', { class: 'd-flex' })
  var $clearBtn = $('<a />', { href: '#' })
    .text('clear')
    .on('click', function (e) {
      e.preventDefault()
      var $logo = $('.brand-link')
      logo_skins.forEach(function (skin) { $logo.removeClass(skin) })
    })

  var $brandSelect = createSkinBlock(logo_skins, function () {
    var color = $(this).data('color')
    var $logo = $('.brand-link')
    if (color === 'navbar-light' || color === 'navbar-white') {
      $logo.addClass('text-black')
    } else {
      $logo.removeClass('text-black')
    }
    logo_skins.forEach(function (skin) { $logo.removeClass(skin) })
    if (color) {
      $(this).parent()
        .removeClass()
        .addClass('custom-select mb-3 border-0')
        .addClass(color)
        .addClass(color !== 'navbar-light' && color !== 'navbar-white' ? 'text-light' : '')
    } else {
      $(this).parent().removeClass().addClass('custom-select mb-3 border-0')
    }
    $logo.addClass(color)
  }, true).append($clearBtn)
  $brandSelect.attr('data-storage-key', 'brandVariant')
  $logoWrapper.append($brandSelect)
  $container.append($logoWrapper)

  var activeBrandColor = null
  $('.brand-link')[0].classList.forEach(function (className) {
    if (logo_skins.indexOf(className) > -1 && activeBrandColor === null) {
      activeBrandColor = className.replace('navbar-', 'bg-')
    }
  })
  if (activeBrandColor) {
    $brandSelect.find('option.' + activeBrandColor).prop('selected', true)
    $brandSelect
      .removeClass()
      .addClass('custom-select mb-3 text-light border-0 ' + activeBrandColor)
  }

  // ==================================================================
  //  FUNGSI LOCALSTORAGE UNTUK MENERAPKAN DAN MENYIMPAN
  // ==================================================================

  /**
   * Menerapkan nilai dari localStorage ke elemen kontrol.
   * Untuk checkbox: mengatur checked dan memicu event change.
   * Untuk select: mengatur value dan memicu event change.
   */
  function applyLocalStorageToUI() {
    // Checkbox
    $('.control-sidebar input[type="checkbox"][data-storage-key]').each(function () {
      var $cb = $(this)
      var key = $cb.data('storage-key')
      var saved = localStorage.getItem(key)
      if (saved !== null) {
        var shouldBeChecked = saved === 'true'
        if ($cb.prop('checked') !== shouldBeChecked) {
          $cb.prop('checked', shouldBeChecked).trigger('change')
        }
      }
    })

    // Select
    $('.control-sidebar select[data-storage-key]').each(function () {
      var $select = $(this)
      var key = $select.data('storage-key')
      var saved = localStorage.getItem(key)
      if (saved) {
        $select.val(saved).trigger('change')
      }
    })
  }

  /**
   * Memasang listener untuk menyimpan perubahan ke localStorage.
   */
  function setupSaveListeners() {
    // Checkbox change
    $('.control-sidebar input[type="checkbox"][data-storage-key]').on('change', function () {
      var $cb = $(this)
      var key = $cb.data('storage-key')
      localStorage.setItem(key, $cb.is(':checked'))
    })

    // Select change
    $('.control-sidebar select[data-storage-key]').on('change', function () {
      var $select = $(this)
      var key = $select.data('storage-key')
      localStorage.setItem(key, $select.val())
    })
  }

  /**
   * Menambahkan tombol reset yang menghapus semua kunci localStorage
   * dan me-refresh halaman.
   */
  function addResetButton() {
    var $resetBtn = $('<button />', {
      class: 'btn btn-secondary btn-block mt-3',
      id: 'resetCustomize',
      html: '<i class="fas fa-undo"></i> Reset ke Default'
    }).on('click', function (e) {
      e.preventDefault()
      $('.control-sidebar [data-storage-key]').each(function () {
        var key = $(this).data('storage-key')
        localStorage.removeItem(key)
      })
      window.location.reload()
    })
    $('.control-sidebar-content').append($resetBtn)
  }

  // ==================================================================
  //  INISIALISASI
  // ==================================================================
  loadSettings()                // Terapkan langsung class dari localStorage
  addResetButton()              // Tambah tombol reset
  setupSaveListeners()          // Pasang listener untuk menyimpan
  applyLocalStorageToUI()       // Sinkronkan UI dengan localStorage (centang dll.)

})(jQuery)