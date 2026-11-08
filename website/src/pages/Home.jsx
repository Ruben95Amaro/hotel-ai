import React from 'react'
import { Link } from 'react-router-dom'
import { Search, MapPin, Star, Waves, Building2, Sparkles, ArrowRight, Calendar, Users } from 'lucide-react'

const features = [
  {
    icon: Waves,
    title: 'Ocean View Rooms',
    description: 'Wake up to breathtaking Atlantic Ocean views from your private balcony.',
  },
  {
    icon: Star,
    title: 'World-Class Service',
    description: '24/7 concierge, room service, and personalized attention to every detail.',
  },
  {
    icon: Building2,
    title: 'Luxury Amenities',
    description: 'Spa, infinity pool, fine dining, fitness center, and business facilities.',
  },
  {
    icon: Sparkles,
    title: 'Prime Location',
    description: 'Walking distance to historic landmarks, shopping, and cultural attractions.',
  },
]

const stats = [
  { value: '150+', label: 'Luxury Rooms' },
  { value: '4.9/5', label: 'Guest Rating' },
  { value: '24/7', label: 'Concierge' },
  { value: '5★', label: 'Rating' },
]

export default function Home() {
  return (
    <div>
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center bg-gradient-to-br from-primary-900 via-primary-800 to-primary-900 overflow-hidden">
        <div className="absolute inset-0 bg-[url('/hero-pattern.svg')] opacity-5" />
        <div className="absolute inset-0 bg-black/30" />
        <div className="container-custom relative z-10 py-20 lg:py-32">
          <div className="max-w-3xl mx-auto text-center">
            <span className="inline-block px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-white text-sm font-medium mb-6">
              🏆 Voted Best Luxury Hotel in Lisbon 2024
            </span>
            <h1 className="font-display text-5xl lg:text-7xl font-medium text-white mb-6 text-balance leading-tight">
              Experience Unparalleled Luxury at <br />
              <span className="text-primary-200">Grand Ocean Hotel</span>
            </h1>
            <p className="text-lg lg:text-xl text-primary-100 mb-10 max-w-2xl mx-auto leading-relaxed">
              Where Atlantic elegance meets Portuguese hospitality. Create unforgettable memories in the heart of Lisbon.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <Link
                to="/rooms"
                className="btn-primary text-lg px-8 py-4 group"
              >
                Explore Rooms & Suites
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                to="/services"
                className="btn bg-white/10 text-white border-white/30 hover:bg-white/20 text-lg px-8 py-4"
              >
                View Services
              </Link>
            </div>

            {/* Search Widget */}
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 lg:p-8 border border-white/20 max-w-2xl mx-auto">
              <Link to="/rooms" className="block">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-left">
                    <label className="block text-xs font-medium text-primary-200 uppercase tracking-wide mb-1">Check-in</label>
                    <div className="flex items-center bg-white/10 rounded-lg px-4 py-3 border border-white/20">
                      <Calendar className="h-5 w-5 text-primary-300 mr-3" />
                      <span className="text-white font-medium">Select date</span>
                    </div>
                  </div>
                  <div className="text-left">
                    <label className="block text-xs font-medium text-primary-200 uppercase tracking-wide mb-1">Check-out</label>
                    <div className="flex items-center bg-white/10 rounded-lg px-4 py-3 border border-white/20">
                      <Calendar className="h-5 w-5 text-primary-300 mr-3" />
                      <span className="text-white font-medium">Select date</span>
                    </div>
                  </div>
                  <div className="text-left">
                    <label className="block text-xs font-medium text-primary-200 uppercase tracking-wide mb-1">Guests</label>
                    <div className="flex items-center bg-white/10 rounded-lg px-4 py-3 border border-white/20">
                      <Users className="h-5 w-5 text-primary-300 mr-3" />
                      <span className="text-white font-medium">2 Guests, 1 Room</span>
                    </div>
                  </div>
                  <div className="text-left">
                    <label className="block text-xs font-medium text-primary-200 uppercase tracking-wide mb-1">Rooms</label>
                    <div className="flex items-center bg-white/10 rounded-lg px-4 py-3 border border-white/20">
                      <Search className="h-5 w-5 text-primary-300 mr-3" />
                      <span className="text-white font-medium">1 Room</span>
                    </div>
                  </div>
                </div>
                <button className="w-full mt-6 btn-primary py-4 text-lg font-semibold">
                  Check Availability
                </button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-white py-16 lg:py-24">
        <div className="container-custom">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="font-display text-4xl lg:text-5xl font-bold text-primary-600 mb-2">{stat.value}</div>
                <div className="text-gray-600 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-gray-50 py-16 lg:py-24">
        <div className="container-custom">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="font-display text-3xl lg:text-4xl font-medium text-gray-900 mb-4">
              Why Choose Grand Ocean Hotel
            </h2>
            <p className="text-lg text-gray-600">
              Every detail is crafted to ensure your stay exceeds expectations.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature) => (
              <div key={feature.title} className="card p-6 lg:p-8 text-center hover:shadow-lg">
                <div className="w-16 h-16 mx-auto mb-6 bg-primary-100 rounded-2xl flex items-center justify-center">
                  <feature.icon className="h-8 w-8 text-primary-600" />
                </div>
                <h3 className="font-display text-xl font-medium text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-primary-600 py-16 lg:py-24">
        <div className="container-custom text-center">
          <h2 className="font-display text-3xl lg:text-4xl font-medium text-white mb-4">
            Ready for an Unforgettable Stay?
          </h2>
          <p className="text-primary-100 mb-8 max-w-2xl mx-auto">
            Book now and enjoy exclusive benefits including complimentary breakfast, spa access, and late checkout.
          </p>
          <Link to="/rooms" className="btn bg-white text-primary-600 hover:bg-primary-50 px-8 py-4 text-lg">
            Book Your Stay
          </Link>
        </div>
      </section>
    </div>
  )
}