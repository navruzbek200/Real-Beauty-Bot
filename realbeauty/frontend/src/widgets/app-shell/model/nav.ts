export interface NavItem {
  to: string
  label: string
  permission?: string
  superuserOnly?: boolean
}

export interface NavSection {
  title: string
  items: NavItem[]
}

// Mirrors the old Unfold admin's sidebar grouping, so the move to the SPA
// doesn't also relearn where everything lives.
export const NAV_SECTIONS: NavSection[] = [
  {
    title: 'Asosiy',
    items: [
      { to: '/', label: 'Boshqaruv paneli' },
      { to: '/customers', label: 'Xaridorlar', permission: 'users.view_telegramuser' },
      { to: '/support-threads', label: 'Murojaatlar', permission: 'support.view_supportthread' },
    ],
  },
  {
    title: 'Mahsulotlar',
    items: [
      { to: '/products', label: 'Mahsulotlar', permission: 'products.view_product' },
      { to: '/top-products', label: 'Bu oydagi top', permission: 'products.view_product' },
      {
        to: '/tutorial-steps',
        label: 'Video darsliklar',
        permission: 'products.view_producttutorialstep',
      },
      { to: '/user-products', label: 'Sotib olingan mahsulotlar', permission: 'users.view_userproduct' },
    ],
  },
  {
    title: 'Marketing',
    items: [
      { to: '/auto-messages', label: 'Avtomatik xabarlar', permission: 'campaigns.view_automessage' },
      { to: '/broadcasts', label: "E'lonlar", permission: 'campaigns.view_broadcast' },
      { to: '/message-templates', label: 'Xabar shablonlari', permission: 'campaigns.view_messagetemplate' },
      { to: '/discounts', label: 'Chegirmalar', permission: 'bot_settings.view_discount' },
      { to: '/campaign-logs', label: 'Yuborilgan xabarlar', permission: 'campaigns.view_campaignlog' },
      { to: '/auto-message-logs', label: 'Avto xabarlar jurnali', superuserOnly: true },
    ],
  },
  {
    title: 'Bonus dasturi',
    items: [
      { to: '/loyalty-accounts', label: 'Bonus hisoblari', permission: 'loyalty.view_loyaltyaccount' },
      { to: '/rewards', label: "Sovg'alar", permission: 'loyalty.view_reward' },
      {
        to: '/reward-redemptions',
        label: "Almashtirilgan sovg'alar",
        permission: 'loyalty.view_rewardredemption',
      },
      {
        to: '/points-transactions',
        label: 'Ball harakatlari',
        permission: 'loyalty.view_pointstransaction',
      },
      { to: '/loyalty-settings', label: 'Bonus sozlamalari', permission: 'loyalty.view_loyaltysettings' },
    ],
  },
  {
    title: 'Analitika',
    items: [
      { to: '/feedback', label: "Mijozlar fikri / Baholar", permission: 'analytics.view_userfeedback' },
      { to: '/skin-quiz-results', label: 'Teri testi natijalari', permission: 'analytics.view_skinquizresult' },
      { to: '/progress-photos', label: 'Natija rasmlari', permission: 'analytics.view_progressphoto' },
    ],
  },
  {
    title: 'Sozlamalar',
    items: [
      { to: '/global-settings', label: 'Umumiy sozlamalar', superuserOnly: true },
      { to: '/staff', label: 'Xodimlar', superuserOnly: true },
      { to: '/support-settings', label: 'Telegram guruh', superuserOnly: true },
      { to: '/support-admins', label: 'Guruh adminlari', superuserOnly: true },
    ],
  },
]
