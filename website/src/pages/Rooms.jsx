import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { hotelApi } from '../services/api'
import { Star, Waves, Wifi, Coffee, Car, Dumbbell, Flower2 as SpaIcon, Utensils, Loader2, MapPin, ChevronRight, CheckCircle } from 'lucide-react'

const amenityIcons = {
  Wifi: Wifi,
  Coffee: Coffee,
  Car: Car,
  Spa: SpaIcon,
  Utensils: Utensils,
  Star: Star,
  Waves: Waves,
  CheckCircle: CheckCircle,
}

const roomTypes = [
  {
    id: 'standard',
    name: 'Standard Room',
    description: 'Elegant comfort with garden or city views. Perfect for solo travelers or couples.',
    basePrice: 150,
    capacity: 2,
    size: '25 m²',
    beds: '1 King or 2 Twin',
    view: 'Garden/City',
    amenities: ['Free WiFi', 'Air Conditioning', 'Flat-screen TV', 'Minibar', 'Safe', 'En-suite bathroom'],
    features: ['Wifi', 'Coffee', 'Car'],
  },
  {
    id: 'deluxe',
    name: 'Deluxe Room',
    description: 'Spacious rooms with private balcony and partial ocean views. Enhanced amenities.',
    basePrice: 250,
    capacity: 3,
    size: '35 m²',
    beds: '1 King + Sofa bed',
    view: 'Partial Ocean',
    amenities: ['Free WiFi', 'Air Conditioning', 'Flat-screen TV', 'Minibar', 'Safe', 'En-suite bathroom', 'Balcony', 'Bathrobes', 'Premium toiletries'],
    features: ['Waves', 'Wifi', 'Coffee', 'Car', 'Spa'],
  },
  {
    id: 'suite',
    name: 'Junior Suite',
    description: 'Separate living area with stunning ocean views. Luxury bath with soaking tub.',
    basePrice: 400,
    capacity: 4,
    size: '50 m²',
    beds: '1 King + Living room sofa bed',
    view: 'Full Ocean',
    amenities: ['Free WiFi', 'Air Conditioning', 'Flat-screen TV', 'Minibar', 'Safe', 'En-suite bathroom', 'Balcony', 'Bathrobes', 'Premium toiletries', 'Living area', 'Soaking tub', 'Nespresso machine'],
    features: ['Waves', 'Wifi', 'Coffee', 'Car', 'Spa', 'Utensils'],
  },
  {
    id: 'presidential',
    name: 'Presidential Suite',
    description: 'Ultimate luxury with panoramic ocean views, private terrace, butler service.',
    basePrice: 800,
    capacity: 4,
    size: '100 m²',
    beds: '1 King + 2 sofa beds',
    view: 'Panoramic Ocean',
    amenities: ['Free WiFi', 'Air Conditioning', 'Flat-screen TV', 'Minibar', 'Safe', 'En-suite bathroom', 'Private terrace', 'Bathrobes', 'Premium toiletries', 'Living area', 'Soaking tub', 'Nespresso machine', 'Butler service', 'Private check-in', 'Complimentary minibar'],
    features: ['Waves', 'Wifi', 'Coffee', 'Car', 'Flower2', 'Utensils', 'Star'],
  },
]

export default function Rooms() {
  const [rooms, setRooms] = useState(roomTypes)
  const [loading, setLoading] = useState(false)
  const [selectedRoom, setSelectedRoom] = useState(null)
  const [checkIn, setCheckIn] = useState('')
  const [checkOut, setCheckOut] = useState('')
  const [guests, setGuests] = useState(2)
  const navigate = useNavigate()

  useEffect(() => {
    // Fetch rooms from API if needed
    fetchRooms()
  }, [])

  const fetchRooms = async () => {
    try {
      setLoading(true)
      // const response = await hotelApi.getRooms()
      // setRooms(response.data)
    } catch (error) {
      console.error('Failed to fetch rooms:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateNights = () => {
    if (checkIn && checkOut) {
      const start = new Date(checkIn)
      const end = new Date(checkOut)
      const diffTime = Math.abs(end - start)
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    }
    return 1
  }

  const handleBookNow = (room) => {
    if (!checkIn || !checkOut) {
      alert('Please select check-in and check-out dates')
      return
    }
    // Navigate to booking page with room and dates
    navigate(`/booking?room=${room.id}&checkIn=${checkIn}&checkOut=${checkOut}&guests=${guests}`)
  }

  const nights = calculateNights()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <section className="bg-primary-600 py-16 lg:py-24 text-white">
        <div className="container-custom">
          <div className="max-w-2xl">
            <h1 className="font-display text-4xl lg:text-5xl font-medium mb-4">Rooms & Suites</h1>
            <p className="text-primary-100 text-lg">
              Choose from our collection of elegantly appointed rooms and suites, each designed for your ultimate comfort.
            </p>
          </div>
        </div>
      </section>

      {/* Date Selector */}
      <section className="bg-white -mt-8 mb-12">
        <div className="container-custom">
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 lg:p-8">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 items-end">
              <div>
                <label className="label">Check-in</label>
                <input
                  type="date"
                  value={checkIn}
                  onChange={(e) => setCheckIn(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  className="input"
                />
              </div>
              <div>
                <label className="label">Check-out</label>
                <input
                  type="date"
                  value={checkOut}
                  onChange={(e) => setCheckOut(e.target.value)}
                  min={checkIn ? new Date(new Date(checkIn).getTime() + 86400000).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]}
                  className="input"
                />
              </div>
              <div>
                <label className="label">Guests</label>
                <select
                  value={guests}
                  onChange={(e) => setGuests(parseInt(e.target.value))}
                  className="input"
                >
                  {[1, 2, 3, 4].map((g) => (
                    <option key={g} value={g}>{g} Guest{g > 1 ? 's' : ''}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">&nbsp;</label>
                <button
                  onClick={() => {}}
                  className="btn-primary w-full"
                  disabled={loading}
                >
                  {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Search Availability'}
                </button>
              </div>
            </div>
            {checkIn && checkOut && (
              <div className="mt-4 p-4 bg-primary-50 rounded-lg border border-primary-100">
                <p className="text-primary-800 font-medium">
                  Stay: {nights} night{nights > 1 ? 's' : ''} • {guests} Guest{guests > 1 ? 's' : ''}
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Room Cards */}
      <section className="py-12 lg:py-16">
        <div className="container-custom">
          <div className="grid lg:grid-cols-2 xl:grid-cols-2 gap-8">
            {rooms.map((room) => (
              <article key={room.id} className="card group">
                {/* Room Image Placeholder */}
                <div className="relative h-64 lg:h-72 bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center overflow-hidden">
                  <div className="text-center p-8">
                    <div className="text-6xl mb-2">🏨</div>
                    <h3 className="font-display text-2xl font-medium text-primary-800">{room.name}</h3>
                  </div>
                  <div className="absolute top-4 right-4">
                    <span className="bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-primary-700">
                      From €{room.basePrice}/night
                    </span>
                  </div>
                </div>

                <div className="p-6 lg:p-8">
                  <p className="text-gray-600 mb-6 leading-relaxed">{room.description}</p>

                  {/* Quick Specs */}
                  <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                    <div className="text-center">
                      <div className="font-display text-lg font-bold text-gray-900">{room.size}</div>
                      <div className="text-xs text-gray-500">Size</div>
                    </div>
                    <div className="text-center">
                      <div className="font-display text-lg font-bold text-gray-900">{room.beds}</div>
                      <div className="text-xs text-gray-500">Beds</div>
                    </div>
                    <div className="text-center">
                      <div className="font-display text-lg font-bold text-gray-900">{room.capacity}</div>
                      <div className="text-xs text-gray-500">Max Guests</div>
                    </div>
                  </div>

                  {/* Amenities */}
                  <div className="mb-6">
                    <h4 className="font-medium text-gray-900 mb-3 flex items-center space-x-2">
                      <MapPin className="h-4 w-4 text-primary-500" />
                      <span>View: {room.view}</span>
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {room.features.map((feature) => {
                const Icon = amenityIcons[feature] || Wifi
                return (
                  <span key={feature} className="flex items-center space-x-1 px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm">
                    <Icon className="h-4 w-4" />
                    <span>{feature}</span>
                  </span>
                )
              })}
                    </div>
                  </div>

                  {/* Full Amenities List */}
                  <details className="mb-6 group">
                    <summary className="flex items-center justify-between cursor-pointer text-sm font-medium text-gray-700 hover:text-primary-600">
                      <span>All Amenities ({room.amenities.length})</span>
                      <ChevronRight className="h-5 w-5 text-gray-400 transition-transform group-open:rotate-90" />
                    </summary>
                    <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-gray-600">
                      {room.amenities.map((amenity) => (
                        <div key={amenity} className="flex items-center space-x-2">
                          <CheckCircle className="h-4 w-4 text-primary-500 flex-shrink-0" />
                          <span>{amenity}</span>
                        </div>
                      ))}
                    </div>
                  </details>

                  {/* Price & Book */}
                  <div className="border-t border-gray-100 pt-6">
                    <div className="flex items-baseline justify-between mb-4">
                      <div>
                        <span className="font-display text-3xl font-bold text-gray-900">€{room.basePrice * nights}</span>
                        <span className="text-gray-500 ml-2">for {nights} night{nights > 1 ? 's' : ''}</span>
                      </div>
                      <span className="text-sm text-gray-500">€{room.basePrice}/night</span>
                    </div>
                    <Link
                      to={`/booking?room=${room.id}&checkIn=${checkIn}&checkOut=${checkOut}&guests=${guests}`}
                      className="btn-primary w-full text-center"
                    >
                      Book Now
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-primary-600 py-16 lg:py-24 text-white">
        <div className="container-custom text-center">
          <h2 className="font-display text-3xl lg:text-4xl font-medium mb-4">Can't Find What You're Looking For?</h2>
          <p className="text-primary-100 mb-8 max-w-2xl mx-auto">
            Contact our reservations team for custom packages, extended stays, or special arrangements.
          </p>
          <Link to="/about" className="btn bg-white text-primary-600 hover:bg-primary-50 px-8 py-4 text-lg">
            Contact Us
          </Link>
        </div>
      </section>
    </div>
  )
}