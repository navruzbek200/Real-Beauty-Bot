import { Route, Routes } from 'react-router-dom'

import { AppUsersPage } from '@/pages/app-users'
import { AutoMessageLogsPage } from '@/pages/auto-message-logs'
import { AutoMessagesPage } from '@/pages/auto-messages'
import { BroadcastsPage } from '@/pages/broadcasts'
import { CampaignLogsPage } from '@/pages/campaign-logs'
import { CustomersPage } from '@/pages/customers'
import { DashboardPage } from '@/pages/dashboard'
import { DiscountsPage } from '@/pages/discounts'
import { FeedbackPage } from '@/pages/feedback'
import { GlobalSettingsPage } from '@/pages/global-settings'
import { LoginPage } from '@/pages/login'
import { LoyaltyAccountsPage } from '@/pages/loyalty-accounts'
import { LoyaltySettingsPage } from '@/pages/loyalty-settings'
import { MessageTemplatesPage } from '@/pages/message-templates'
import { PointsTransactionsPage } from '@/pages/points-transactions'
import { ProductsPage } from '@/pages/products'
import { ProgressPhotosPage } from '@/pages/progress-photos'
import { RewardRedemptionsPage } from '@/pages/reward-redemptions'
import { RewardsPage } from '@/pages/rewards'
import { SkinQuizResultsPage } from '@/pages/skin-quiz-results'
import { StaffPage } from '@/pages/staff'
import { SupportAdminsPage } from '@/pages/support-admins'
import { SupportSettingsPage } from '@/pages/support-settings'
import { SupportThreadsPage } from '@/pages/support-threads'
import { TopProductsPage } from '@/pages/top-products'
import { UserProductsPage } from '@/pages/user-products'
import { ProtectedRoute } from './protected-route'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />

      <Route
        path="/customers"
        element={<ProtectedRoute permission="users.view_telegramuser"><CustomersPage /></ProtectedRoute>}
      />
      <Route
        path="/app-users"
        element={<ProtectedRoute permission="users.view_appuser"><AppUsersPage /></ProtectedRoute>}
      />
      <Route
        path="/user-products"
        element={<ProtectedRoute permission="users.view_userproduct"><UserProductsPage /></ProtectedRoute>}
      />
      <Route
        path="/support-threads"
        element={<ProtectedRoute permission="support.view_supportthread"><SupportThreadsPage /></ProtectedRoute>}
      />

      <Route
        path="/products"
        element={<ProtectedRoute permission="products.view_product"><ProductsPage /></ProtectedRoute>}
      />
      <Route
        path="/top-products"
        element={<ProtectedRoute permission="products.view_product"><TopProductsPage /></ProtectedRoute>}
      />

      <Route
        path="/auto-messages"
        element={<ProtectedRoute permission="campaigns.view_automessage"><AutoMessagesPage /></ProtectedRoute>}
      />
      <Route
        path="/broadcasts"
        element={<ProtectedRoute permission="campaigns.view_broadcast"><BroadcastsPage /></ProtectedRoute>}
      />
      <Route
        path="/message-templates"
        element={<ProtectedRoute permission="campaigns.view_messagetemplate"><MessageTemplatesPage /></ProtectedRoute>}
      />
      <Route
        path="/discounts"
        element={<ProtectedRoute permission="bot_settings.view_discount"><DiscountsPage /></ProtectedRoute>}
      />
      <Route
        path="/campaign-logs"
        element={<ProtectedRoute permission="campaigns.view_campaignlog"><CampaignLogsPage /></ProtectedRoute>}
      />
      <Route
        path="/auto-message-logs"
        element={<ProtectedRoute superuserOnly><AutoMessageLogsPage /></ProtectedRoute>}
      />

      <Route
        path="/loyalty-accounts"
        element={<ProtectedRoute superuserOnly><LoyaltyAccountsPage /></ProtectedRoute>}
      />
      <Route path="/rewards" element={<ProtectedRoute superuserOnly><RewardsPage /></ProtectedRoute>} />
      <Route
        path="/reward-redemptions"
        element={<ProtectedRoute permission="loyalty.view_rewardredemption"><RewardRedemptionsPage /></ProtectedRoute>}
      />
      <Route
        path="/points-transactions"
        element={<ProtectedRoute superuserOnly><PointsTransactionsPage /></ProtectedRoute>}
      />
      <Route
        path="/loyalty-settings"
        element={<ProtectedRoute superuserOnly><LoyaltySettingsPage /></ProtectedRoute>}
      />

      <Route
        path="/feedback"
        element={<ProtectedRoute permission="analytics.view_userfeedback"><FeedbackPage /></ProtectedRoute>}
      />
      <Route
        path="/skin-quiz-results"
        element={<ProtectedRoute permission="analytics.view_skinquizresult"><SkinQuizResultsPage /></ProtectedRoute>}
      />
      <Route
        path="/progress-photos"
        element={<ProtectedRoute permission="analytics.view_progressphoto"><ProgressPhotosPage /></ProtectedRoute>}
      />

      <Route path="/global-settings" element={<ProtectedRoute superuserOnly><GlobalSettingsPage /></ProtectedRoute>} />
      <Route path="/staff" element={<ProtectedRoute superuserOnly><StaffPage /></ProtectedRoute>} />
      <Route
        path="/support-settings"
        element={<ProtectedRoute superuserOnly><SupportSettingsPage /></ProtectedRoute>}
      />
      <Route
        path="/support-admins"
        element={<ProtectedRoute superuserOnly><SupportAdminsPage /></ProtectedRoute>}
      />
    </Routes>
  )
}
