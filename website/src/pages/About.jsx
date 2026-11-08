import React from 'react'
import { Link } from 'react-router-dom'
import { Waves, Building2, Award, Users, Clock, MapPin, Phone, Mail, Send, Loader2 } from 'lucide-react'
import { useForm } from 'react-hook-form'

export default function About() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <section className="bg-primary-600 py-16 lg:py-24 text-white">
        <div className="container-custom">
          <div className="max-w-2xl">
            <h1 className="font-display text-4xl lg:text-5xl font-medium mb-4">About Grand Ocean Hotel</h1>
            <p className="text-primary-100 text-lg">
              A legacy of Portuguese hospitality meeting Atlantic elegance since 1987.
            </p>
          </div>
        </div>
      </section>

      {/* Story */}
      <section className="py-16 lg:py-24">
        <div className="container-custom">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="font-display text-3xl lg:text-4xl font-medium text-gray-900 mb-6">
                Our Story
              </h2>
              <div className="space-y-4 text-gray-600 leading-relaxed">
                <p>
                  Founded in 1987 by the Silva family, Grand Ocean Hotel began as a vision to create a sanctuary 
                  where the raw beauty of the Atlantic Ocean meets the warmth of Portuguese hospitality.
                </p>
                <p>
                  Perched on the cliffs overlooking the Atlantic, our hotel has welcomed dignitaries, celebrities, 
                  and discerning travelers from around the world. Each guest becomes part of our story — a story 
                  of memorable sunsets, exceptional service, and moments that last a lifetime.
                </p>
                <p>
                  Today, we continue this legacy with 150+luxuriously appointed rooms and suites, world-class dining, 
                  a thalassotherapy spa, and a commitment to sustainable luxury that honors our coastal home.
                </p>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-[4/3] bg-gradient-to-br from-primary-100 to-primary-200 rounded-2xl flex items-center justify-center overflow-hidden">
                <div className="text-center p-8">
                  <div className="text-8xl mb-4">🏨</div>
                  <h3 className="font-display text-2xl font-medium text-primary-800">Grand Ocean Hotel</h3>
                  <p className="text-primary-600 mt-2">Lisbon, Portugal</p>
                </div>
              </div>
              <div className="absolute -bottom-6 -left-6 bg-white p-6 rounded-xl shadow-lg border border-gray-100 max-w-xs">
                <div className="flex items-center space-x-3 mb-3">
                  <Award className="h-8 w-8 text-amber-500" />
                  <div>
                    <div className="font-display text-2xl font-bold text-gray-900">4.9/5</div>
                    <div className="text-sm text-gray-500">Guest Rating</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3 mb-3">
                  <Award className="h-8 w-8 text-primary-500" />
                  <div>
                    <div className="font-display text-2xl font-bold text-gray-900">150+</div>
                    <div className="text-sm text-gray-500">Luxury Rooms</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Clock className="h-8 w-8 text-accent-500" />
                  <div>
                    <div className="font-display text-2xl font-bold text-gray-900">24/7</div>
                    <div className="text-sm text-gray-500">Concierge</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="bg-white py-16 lg:py-24">
        <div className="container-custom">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="font-display text-3xl lg:text-4xl font-medium text-gray-900 mb-4">
              Our Values
            </h2>
            <p className="text-lg text-gray-600">
              The principles that guide every interaction and decision.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { icon: Heart, title: 'Genuine Care', desc: 'We treat every guest like family, anticipating needs before they arise.' },
              { icon: Award, title: 'Excellence', desc: 'Relentless pursuit of perfection in every detail, every day.' },
              { icon: Waves, title: 'Sustainability', desc: 'Protecting our ocean home through responsible luxury practices.' },
              { icon: Users, title: 'Authenticity', desc: 'Celebrating Portuguese culture and local craftsmanship.' },
            ].map((value) => (
              <div key={value.title} className="card p-8 text-center hover:shadow-lg transition-shadow">
                <div className="w-16 h-16 mx-auto mb-6 bg-primary-100 rounded-2xl flex items-center justify-center">
                  <value.icon className="h-8 w-8 text-primary-600" />
                </div>
                <h3 className="font-display text-xl font-medium text-gray-900 mb-3">{value.title}</h3>
                <p className="text-gray-600 leading-relaxed">{value.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="bg-gray-50 py-16 lg:py-24">
        <div className="container-custom">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="font-display text-3xl lg:text-4xl font-medium text-gray-900 mb-4">
              Meet Our Leadership
            </h2>
            <p className="text-lg text-gray-600">
              Passionate hospitality professionals dedicated to your experience.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { name: 'Isabel Silva', role: 'General Manager', bio: '30+ years in luxury hospitality. Former Ritz Paris.', img: '👩‍💼' },
              { name: 'Chef Miguel Costa', role: 'Executive Chef', bio: 'Michelin-starred chef. Champion of Atlantic cuisine.', img: '👨‍🍳' },
              { name: 'Dr. Ana Santos', role: 'Spa Director', bio: 'Thalassotherapy pioneer. PhD in Marine Wellness.', img: '👩‍⚕️' },
            ].map((member) => (
              <div key={member.name} className="card text-center p-8">
                <div className="text-6xl mb-4">{member.img}</div>
                <h3 className="font-display text-xl font-medium text-gray-900 mb-1">{member.name}</h3>
                <p className="text-primary-600 font-medium mb-4">{member.role}</p>
                <p className="text-gray-600 text-sm leading-relaxed">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact CTA */}
      <section className="bg-primary-600 py-16 lg:py-24 text-white">
        <div className="container-custom">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="font-display text-3xl lg:text-4xl font-medium mb-4">Visit Us</h2>
              <p className="text-primary-100 mb-8">
                Experience the magic of Grand Ocean Hotel for yourself. Our team is ready to welcome you.
              </p>
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <MapPin className="h-6 w-6 text-primary-200" />
                  <div>
                    <div className="font-medium">Rua do Ouro 123, 1100-063 Lisbon, Portugal</div>
                    <div className="text-primary-200 text-sm">Overlooking the Tagus River & Atlantic Ocean</div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <Phone className="h-6 w-6 text-primary-200" />
                  <div>
                    <div className="font-medium">+351 (21) 345-6789</div>
                    <div className="text-primary-200 text-sm">Reservations: +351 (21) 345-6780</div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <Mail className="h-6 w-6 text-primary-200" />
                  <div>
                    <div className="font-medium">info@grandoceanhotel.com</div>
                    <div className="text-primary-200 text-sm">reservations@grandoceanhotel.com</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 border border-white/20">
              <h3 className="font-display text-xl font-medium mb-6">Send Us a Message</h3>
              <ContactForm />
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

function ContactForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm()
  const [submitted, setSubmitted] = React.useState(false)

  const onSubmit = async (data) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSubmitted(true)
    setTimeout(() => setSubmitted(false), 3000)
  }

  if (submitted) {
    return (
      <div className="text-center py-8">
        <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
          <CheckCircle className="h-8 w-8 text-green-600" />
        </div>
        <h4 className="font-medium text-white mb-2">Message Sent!</h4>
        <p className="text-primary-200">We'll get back to you within 24 hours.</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid sm:grid-cols-2 gap-4">
        <div>
          <label className="label text-white">First Name</label>
          <input {...register('firstName', { required: true })} className="input bg-white/10 border-white/20 text-white placeholder:text-primary-200 focus:border-primary-400" placeholder="John" />
          {errors.firstName && <p className="text-red-400 text-sm mt-1">Required</p>}
        </div>
        <div>
          <label className="label text-white">Last Name</label>
          <input {...register('lastName', { required: true })} className="input bg-white/10 border-white/20 text-white placeholder:text-primary-200 focus:border-primary-400" placeholder="Doe" />
          {errors.lastName && <p className="text-red-400 text-sm mt-1">Required</p>}
        </div>
      </div>
      <div>
        <label className="label text-white">Email</label>
        <input {...register('email', { required: true, pattern: /^\S+@\S+$/i })} className="input bg-white/10 border-white/20 text-white placeholder:text-primary-200 focus:border-primary-400" placeholder="john@example.com" />
        {errors.email && <p className="text-red-400 text-sm mt-1">Valid email required</p>}
      </div>
      <div>
        <label className="label text-white">Message</label>
        <textarea {...register('message', { required: true })} rows={4} className="input bg-white/10 border-white/20 text-white placeholder:text-primary-200 focus:border-primary-400" placeholder="How can we help you?" />
        {errors.message && <p className="text-red-400 text-sm mt-1">Required</p>}
      </div>
      <button type="submit" disabled={isSubmitting} className="btn-primary w-full py-3">
        {isSubmitting ? <Loader2 className="h-5 w-5 animate-spin mx-auto" /> : 'Send Message'}
      </button>
    </form>
  )
}