import React, { useState, useEffect } from 'react'
import { hotelApi } from '../services/api'
import { Waves, Utensils, Flower2 as Spa, Dumbbell, Car, Wifi, ConciergeBell, ShoppingBag, Baby, Sparkles, Loader2, CheckCircle } from 'lucide-react'

const servicesData = [
  {
    id: 'dining',
    icon: Utensils,
    title: 'Fine Dining',
    description: 'Experience culinary excellence at our Michelin-starred restaurant Ocean\'s Bounty, featuring fresh Atlantic seafood and Portuguese-inspired cuisine.',
    features: ['Ocean\'s Bounty Restaurant', 'Sea Breeze Bar & Terrace', 'In-Room Dining 24/7', 'Private Dining Rooms', 'Wine Cellar Tastings'],
    hours: '6:30 AM - 11:00 PM',
    location: 'Ground Floor & Rooftop',
  },
  {
    id: 'spa',
    icon: Spa,
    title: 'Ocean Wellness Spa',
    description: 'Rejuvenate body and mind with our signature treatments inspired by the healing powers of the Atlantic Ocean.',
    features: ['Signature Ocean Rituals', 'Thalassotherapy Pool', 'Sauna & Steam Rooms', 'Couples Treatment Suites', 'Fitness Center 24/7', 'Yoga & Meditation Classes'],
    hours: '9:00 AM - 9:00 PM',
    location: 'Level -1',
  },
  {
    id: 'concierge',
    icon: ConciergeBell,
    title: 'Personal Concierge',
    description: 'Our dedicated concierge team curates unforgettable experiences tailored to your preferences.',
    features: ['Private Tours & Excursions', 'Restaurant Reservations', 'Event Tickets', 'Transportation Arrangements', 'Special Occasion Planning', 'Local Expert Recommendations'],
    hours: '24/7',
    location: 'Lobby',
  },
  {
    id: 'pool',
    icon: Waves,
    title: 'Infinity Pool & Terrace',
    description: 'Our stunning rooftop infinity pool merges with the Atlantic horizon, offering the perfect setting for relaxation.',
    features: ['Heated Infinity Pool', 'Poolside Bar Service', 'Private Cabanas', 'Sunset Cocktail Hour', 'Poolside Light Bites', 'Towel & Robe Service'],
    hours: '7:00 AM - 10:00 PM',
    location: 'Rooftop (Level 8)',
  },
  {
    id: 'business',
    icon: Sparkles,
    title: 'Business & Events',
    description: 'State-of-the-art facilities for meetings, conferences, and celebrations with panoramic ocean views.',
    features: ['5 Meeting Rooms', 'Grand Ballroom (300 guests)', 'Advanced AV Technology', 'Dedicated Event Planner', 'Custom Catering Menus', 'High-Speed Internet'],
    hours: 'By Appointment',
    location: 'Levels 1-2',
  },
  {
    id: 'family',
    icon: Baby,
    title: 'Family Services',
    description: 'Thoughtful amenities and activities to ensure our youngest guests have a magical stay.',
    features: ['Kids\' Club (4-12 years)', 'Babysitting Services', 'Children\'s Menu', 'Family Pool Hours', 'Welcome Gifts for Kids', 'Connecting Rooms Available'],
    hours: '9:00 AM - 6:00 PM',
    location: 'Level 3',
  },
]

export default function Services() {
  const [services, setServices] = useState(servicesData)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('all')

  useEffect(() => {
    fetchServices()
  }, [])

  const fetchServices = async () => {
    try {
      setLoading(true)
      // const response = await hotelApi.getServices()
      // setServices(response.data)
    } catch (error) {
      console.error('Failed to fetch services:', error)
    } finally {
      setLoading(false)
    }
  }

  const categories = ['all', 'dining', 'wellness', 'concierge', 'recreation', 'business', 'family']

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <section className="bg-primary-600 py-16 lg:py-24 text-white">
        <div className="container-custom">
          <div className="max-w-2xl">
            <h1 className="font-display text-4xl lg:text-5xl font-medium mb-4">Hotel Services</h1>
            <p className="text-primary-100 text-lg">
              Discover our world-class amenities and personalized services designed to make your stay extraordinary.
            </p>
          </div>
        </div>
      </section>

      {/* Category Tabs */}
      <section className="bg-white -mt-8 mb-12">
        <div className="container-custom px-4">
          <div className="flex flex-wrap gap-2 overflow-x-auto pb-4 -mx-4 px-4">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveTab(cat)}
                className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all duration-200 ${
                  activeTab === cat
                    ? 'bg-primary-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Services Grid */}
      <section className="py-12 lg:py-16">
        <div className="container-custom">
          <div className="grid lg:grid-cols-2 gap-8">
            {services
              .filter((service) => activeTab === 'all' || service.id === activeTab)
              .map((service) => (
                <article key={service.id} className="card overflow-hidden group">
                  <div className="relative h-56 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
                    <service.icon className="h-16 w-16 text-primary-600 opacity-90 group-hover:scale-110 transition-transform duration-300" />
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-primary-900/80 to-transparent p-6 text-white">
                      <h3 className="font-display text-xl font-medium">{service.title}</h3>
                    </div>
                  </div>
                  <div className="p-6 lg:p-8">
                    <p className="text-gray-600 mb-6 leading-relaxed">{service.description}</p>
                    
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <service.icon className="h-5 w-5 text-primary-500" />
                        <div>
                          <div className="text-xs text-gray-500">Hours</div>
                          <div className="font-medium text-gray-900">{service.hours}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <MapPin className="h-5 w-5 text-primary-500" />
                        <div>
                          <div className="text-xs text-gray-500">Location</div>
                          <div className="font-medium text-gray-900">{service.location}</div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      {service.features.map((feature) => (
                        <div key={feature} className="flex items-center space-x-3">
                          <CheckCircle className="h-5 w-5 text-primary-500 flex-shrink-0" />
                          <span className="text-gray-700">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </article>
              )
            )}
          </div>
        </div>
      </section>

      {/* Additional Amenities */}
      <section className="bg-white py-16 lg:py-24">
        <div className="container-custom">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="font-display text-3xl lg:text-4xl font-medium text-gray-900 mb-4">
              Additional Amenities
            </h2>
            <p className="text-lg text-gray-600">
              Complimentary services included with your stay.
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { icon: Wifi, title: 'High-Speed WiFi', desc: 'Throughout the hotel' },
              { icon: Car, title: 'Valet Parking', desc: '24/7 secure parking' },
              { icon: ShoppingBag, title: 'Shopping Arcade', desc: 'Luxury boutiques' },
              { icon: Sparkles, title: 'Daily Housekeeping', desc: 'Twice daily service' },
            ].map((amenity) => (
              <div key={amenity.title} className="card p-6 text-center hover:shadow-lg transition-shadow">
                <div className="w-14 h-14 mx-auto mb-4 bg-primary-100 rounded-xl flex items-center justify-center">
                  <amenity.icon className="h-7 w-7 text-primary-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-1">{amenity.title}</h4>
                <p className="text-sm text-gray-500">{amenity.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}