import { NavLink } from 'react-router-dom'
import {
  HomeIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  DocumentIcon,
  ChatBubbleLeftRightIcon,
  FolderIcon,
  ChartBarIcon,
  CogIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Plaintiffs', href: '/plaintiffs', icon: UserGroupIcon },
  { name: 'Law Firms', href: '/law-firms', icon: BuildingOfficeIcon },
  { name: 'Cases', href: '/cases', icon: FolderIcon },
  { name: 'Communications', href: '/communications', icon: ChatBubbleLeftRightIcon },
  { name: 'Documents', href: '/documents', icon: DocumentIcon },
  { name: 'Reports', href: '/reports', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
]

export function Sidebar() {
  return (
    <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
      <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white border-r border-gray-200 px-6 pb-4">
        <div className="flex h-16 shrink-0 items-center">
          <div>
            <h1 className="text-xl font-bold text-gray-900">FundingCRM</h1>
            <p className="text-xs text-gray-500 mt-0.5">Pre-Settlement Platform</p>
          </div>
        </div>
        <nav className="flex flex-1 flex-col">
          <ul role="list" className="flex flex-1 flex-col gap-y-7">
            <li>
              <ul role="list" className="-mx-2 space-y-1">
                {navigation.map((item) => (
                  <li key={item.name}>
                    <NavLink
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold ${
                          isActive
                            ? 'bg-primary-50 text-primary-600'
                            : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                        }`
                      }
                    >
                      <item.icon
                        className="h-6 w-6 shrink-0"
                        aria-hidden="true"
                      />
                      {item.name}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  )
}