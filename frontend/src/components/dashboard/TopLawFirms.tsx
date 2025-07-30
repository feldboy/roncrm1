export function TopLawFirms() {
  const lawFirms = [
    {
      id: 1,
      name: 'Johnson & Associates',
      referrals: 0,
      status: 'active'
    },
    {
      id: 2,
      name: 'Smith Legal Group',
      referrals: 0,
      status: 'active'
    },
    {
      id: 3,
      name: 'Davis & Partners LLP',
      referrals: 0,
      status: 'pending'
    }
  ]

  return (
    <div className="card">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="section-heading">Top Law Firms</h2>
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            View All Firms →
          </button>
        </div>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          {lawFirms.map((firm) => (
            <div key={firm.id} className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">{firm.name}</p>
                <p className="text-xs text-gray-500">{firm.referrals} referrals</p>
              </div>
              <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                firm.status === 'active' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {firm.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}